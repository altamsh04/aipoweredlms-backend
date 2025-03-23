from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .ragchat import get_rag_response, get_rag_quiz
from .pptjson import extract_text_from_pdf, generate_json_with_gemini
from rest_framework.decorators import parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from .equation import get_curve_equation
from django.conf import settings
import os
from .upload import upload_file_to_s3
from .summerization import query_pdf_with_gemini

@api_view(['POST'])
def chat_api(request):
    try:
        user_input = request.data.get('prompt')
        if not user_input:
            return Response({
                'status': 'error',
                'message': 'No input provided'
            }, status=400)

        chat_response = get_rag_response(user_input)
        return Response({
            'status': 'success',
            'response': chat_response
        })

    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=500)

@api_view(['POST'])
def quiz_api(request):
    try:
        user_input = request.data.get('prompt')
        if not user_input:
            return Response({
                'status': 'error',
                'message': 'No input provided'
            }, status=400)

        quiz_response = get_rag_quiz(user_input)
        return Response({
            'status': 'success',
            'mcqs': quiz_response
        })

    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=500)


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_pdf(request):
    try:
        pdf_file = request.FILES.get('file')
        if not pdf_file:
            return Response({'status': 'error', 'message': 'No file provided'}, status=400)
        
        # Save the uploaded file temporarily
        temp_pdf_path = os.path.join(settings.MEDIA_ROOT, pdf_file.name)
        with open(temp_pdf_path, 'wb') as temp_pdf:
            for chunk in pdf_file.chunks():
                temp_pdf.write(chunk)
        
        # Extract text from the uploaded PDF
        extracted_text = extract_text_from_pdf(temp_pdf_path)
        if not extracted_text:
            return Response({'status': 'error', 'message': 'Failed to extract text'}, status=400)
        
        # Generate structured JSON using Gemini AI
        structured_json = generate_json_with_gemini(extracted_text)
        
        return Response({'status': 'success', 'data': structured_json})
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)

@api_view(['POST'])
def get_equation(request):
    try:
        curve_name = request.data.get('curve_name')
        equation = get_curve_equation(curve_name)
        return Response({'status': 'success', 'equation': equation})
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)
    
@api_view(['POST'])
def upload_file(request):
    try:
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'status': 'error', 'message': 'No file provided'}, status=400)

        # Upload file to S3
        upload_result = upload_file_to_s3(file_obj)
        if not upload_result['status']:
            return Response({'status': 'error', 'message': upload_result['error']}, status=500)
        
        return Response({'status': 'success', 'url': upload_result['url']})
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)

@api_view(['POST'])
def summarize_pdf(request):
    try:
        user_query = request.data.get('user_query')
        if not user_query:  
            return Response({'status': 'error', 'message': 'No user query provided'}, status=400)
        
        pdf_file = request.FILES.get('file')
        if not pdf_file:
            return Response({'status': 'error', 'message': 'No file provided'}, status=400)
        
        # Save the uploaded file temporarily
        temp_pdf_path = os.path.join(settings.MEDIA_ROOT, pdf_file.name)
        with open(temp_pdf_path, 'wb') as temp_pdf:
            for chunk in pdf_file.chunks():
                temp_pdf.write(chunk)
        
        # Extract text from the uploaded PDF    
        extracted_text = extract_text_from_pdf(temp_pdf_path)
        if not extracted_text:
            return Response({'status': 'error', 'message': 'Failed to extract text'}, status=400)
        
        # Generate summary using Gemini AI
        summary = query_pdf_with_gemini(extracted_text, user_query)
        
        return Response({'status': 'success', 'summary': summary})
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)


# Optional: Add a home view
def home(request):
    return JsonResponse({
        "message": "Welcome to AI Powered LMS API",
        "endpoints": {
            "POST /api/chat/": "Submit prompt to chat system",
            "POST /api/quiz/": "Generate quiz questions",
            "POST /api/upload_pdf/": "Upload a PDF to extract structured JSON",
            "POST /api/equation/": "Get the equation of a curve",
            "POST /api/summerize_pdf/": "Summerize a PDF",
            "POST /api/upload_file/": "Upload a file to S3"
        }
    })