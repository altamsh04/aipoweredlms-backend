import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

def get_curve_equation(curve_name):
    """Generates only the mathematical equation of the given curve using streaming."""
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"Provide only the mathematical equation for the curve: {curve_name}. No extra text."

    response = model.generate_content(prompt, stream=True)  # Enable streaming
    equation = "".join(chunk.text for chunk in response)  # Collect streamed response
    return equation.strip()

if __name__ == "__main__":
    curve_name = input().strip().lower()  # Ask for input without extra text
    print(get_curve_equation(curve_name))  # Print only the equation
