import os
import fitz  # PyMuPDF for extracting text from PDFs
import google.generativeai as genai
from dotenv import load_dotenv
from django.http import JsonResponse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

def extract_text_from_pdf(pdf_path):
    """Extracts text from a text-based PDF (no OCR needed)."""
    text = ""
    try:
        doc = fitz.open(pdf_path)
        text = "\n".join([page.get_text("text") for page in doc])
    except Exception as e:
        print(f"Error extracting text: {e}")
    return text.strip()

def generate_json_with_gemini(pdf_text):
    """Sends extracted PDF text to Gemini and returns the structured JSON response."""
    model = genai.GenerativeModel("gemini-1.5-pro")
    
    fixed_query = f"""
    I want you to go through every single topic and make it one JSON key.  
    Then, go through every subpoint of that unit and write a **detailed description**  
    for each point in the "subpoints" section.  
    Next, go to the next topic (1, 2, 3, ... till the last one).  
    **Ensure the JSON is as detailed as possible**.

    **Here is the document content:**
    {pdf_text[:5000]}  # Limiting input size.

    **Return only valid JSON output. Do not include any extra text or explanations.**
    """
    
    response = model.generate_content(fixed_query)
    json_output = response.text.strip()
    
    # Remove triple backticks if Gemini adds them
    if json_output.startswith("```json"):
        json_output = json_output[7:]  # Remove ```json
    if json_output.endswith("```"):
        json_output = json_output[:-3]  # Remove closing ```
    
    return json_output
