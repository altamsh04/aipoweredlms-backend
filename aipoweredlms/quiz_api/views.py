from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .ragchat import get_rag_response, get_rag_quiz

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

# Optional: Add a home view
def home(request):
    return JsonResponse({
        "message": "Welcome to AI Powered LMS API",
        "endpoints": {
            "POST /api/chat/": "Submit prompt to chat system",
            "POST /api/quiz/": "Generate quiz questions"
        }
    })