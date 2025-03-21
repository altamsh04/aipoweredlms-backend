import os
import io
import json
import re
import boto3
from dotenv import load_dotenv  # Load .env files
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

# Load environment variables from .env file
load_dotenv()

# Get API keys from .env
API_KEY = os.getenv("GOOGLE_API_KEY")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")

if not API_KEY:
    raise ValueError("GOOGLE_API_KEY is missing from .env file!")
if not AWS_ACCESS_KEY or not AWS_SECRET_KEY or not BUCKET_NAME:
    raise ValueError("AWS credentials or bucket name missing from .env file!")

# Initialize S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

# Get list of PDFs from S3 bucket
data = []
response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix='pdfs/')
for obj in response.get('Contents', []):
    if obj['Key'].endswith('.pdf'):
        # Download PDF from S3
        pdf_obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=obj['Key'])
        pdf_content = pdf_obj['Body'].read()
        
        # Create a temporary file-like object
        pdf_file = io.BytesIO(pdf_content)
        
        # Save BytesIO to temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            temp_pdf.write(pdf_content)
            temp_path = temp_pdf.name
        
        # Load PDF content using file path
        loader = PyPDFLoader(temp_path)
        data.extend(loader.load())
        
        # Clean up temp file
        os.unlink(temp_path)

# Split documents
text_splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=500)
docs = text_splitter.split_documents(data)

# Create embeddings
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Store in ChromaDB
vectorstore = Chroma.from_documents(
    documents=docs, 
    embedding=embeddings,
    persist_directory="./vector_db"
)

# Define retriever
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 15})

# LLM setup for chat
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.5, max_tokens=800)

# LLM setup for quiz
quiz_llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.7, max_tokens=4000, response_format="json")

# Improved prompt for chat
system_prompt = (
    "You are an AI assistant designed for in-depth Q&A based on the provided context. "
    "Use the retrieved information to generate detailed and structured responses. "
    "Expand on key concepts, provide explanations, and include relevant examples where necessary. "
    "If the context is insufficient, acknowledge it and suggest possible directions."
    "\n\nContext:\n{context}"
)

# Chat prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
])

# MCQ Prompt Template
mcq_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an AI MCQ generator. Your response MUST be STRICT JSON."),
    ("human", 
        """
        Generate multiple-choice questions (MCQs) on the topic "{topic}" with {difficulty} difficulty.
        Generate a dynamic number of questions based on content richness.
        
        **Strict Difficulty Assignment:**
        - If 'Easy', all MCQs must be in range (1-3).
        - If 'Medium', all MCQs must be in range (4-6).
        - If 'Hard', all MCQs must be in range (7-10).

        **Format Response as JSON:**
        {{
          "mcqs": [
            {{
              "question": "What is AI?",
              "options": {{"A": "Artificial Intelligence", "B": "Automated Input", "C": "Analog Information", "D": "None"}},
              "answer": "A",
              "difficulty": 7
            }}
          ]
        }}

        **IMPORTANT:** 
        - Return JSON ONLY.
        - No explanations, comments, or extra text.
        """
    )
])

# Chains for chat
question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

def get_rag_response(user_input: str) -> str:
    """Fetches a response from the RAG model for the given user input."""
    response = rag_chain.invoke({"input": user_input})

    if "answer" not in response or not response["answer"].strip():
        return "I couldn't find an answer from your documents."
    
    return response["answer"]

def parse_user_input(query):
    """Extracts topic and difficulty from user input."""
    match = re.search(r"(easy|medium|hard)", query, re.IGNORECASE)
    difficulty = match.group(1).capitalize() if match else "Medium"
    topic = re.sub(r"\b(easy|medium|hard)\b", "", query, flags=re.IGNORECASE).strip()
    return topic, difficulty

def generate_mcqs(topic, text, difficulty):
    """Generate MCQs using LLM based on the specified topic dynamically."""
    for attempt in range(3):
        try:
            response = quiz_llm.invoke(mcq_prompt.invoke({
                "topic": topic, 
                "context": text,
                "difficulty": difficulty
            }))
            response_text = response.content if hasattr(response, "content") else str(response)
            response_text = re.sub(r"```json\n|\n```", "", response_text).strip()
            mcqs_data = json.loads(response_text)

            if isinstance(mcqs_data, dict) and "mcqs" in mcqs_data and len(mcqs_data["mcqs"]) > 0:
                return mcqs_data["mcqs"]
            
            print(f"⚠️ Invalid MCQ response format. Retrying... ({attempt+1}/3)")
        except json.JSONDecodeError:
            print("⚠️ JSON Parsing Error. Retrying...")
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")
            break
    return []

def get_rag_quiz(query: str) -> list:
    """Generates MCQs based on the query using RAG."""
    topic, difficulty = parse_user_input(query)
    
    relevant_docs = retriever.invoke(topic)
    if not relevant_docs:
        print(f"❌ No relevant content found for topic: {topic}")
        return []
    
    extracted_text = " ".join([doc.page_content for doc in relevant_docs])
    mcq_list = generate_mcqs(topic, extracted_text, difficulty)
    
    if not mcq_list:
        print("❌ No valid MCQs generated. Try modifying the topic.")
        return []
    
    return mcq_list
