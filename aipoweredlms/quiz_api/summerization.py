import os
import fitz  # PyMuPDF for extracting text from PDFs
import google.generativeai as genai
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

# 🔹 Set PDF Path Directly
PDF_PATH = r"D:\Project-Hackathon\pdfs\Enhancing Classification of Imbalanced Data.pdf"

def extract_text_from_pdf(pdf_path):
    """Extracts text from a text-based PDF (no OCR needed)."""
    text = ""
    try:
        doc = fitz.open(pdf_path)
        text = "\n".join([page.get_text("text") for page in doc])
    except Exception as e:
        print(f"Error extracting text: {e}")
    return text.strip()

def query_pdf_with_gemini(pdf_text, user_query):
    """Queries Gemini about the PDF content."""
    model = genai.GenerativeModel("gemini-1.5-pro")  # Use Flash if Pro is slow

    prompt = f"""
    You are an AI that answers questions based on a provided document.
    
    **Document Content:**
    {pdf_text[:5000]}  # Limit text input to fit within Gemini's context
    
    **User Query:** {user_query}
    Answer based only on the provided document.
    """

    response = model.generate_content(prompt)
    return response.text.strip()

if __name__ == "__main__":
    if not os.path.exists(PDF_PATH):
        print("❌ Error: PDF file not found.")
    else:
        extracted_text = extract_text_from_pdf(PDF_PATH)

        if extracted_text:
            user_query = input("\n🔹 Enter your question about the PDF: ").strip()
            print("\n💡 Answer:", query_pdf_with_gemini(extracted_text, user_query))
        else:
            print("❌ No text extracted from PDF.")
