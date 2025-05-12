from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from apps.study_plan.llm_utils import get_chat_response
import json

@login_required
def intellichat(request):
    return render(request, 'intellichat/index.html')

@login_required
@require_http_methods(['POST'])
def chat_message(request):
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        # Get response using Gemini model
        assistant_message = get_chat_response(user_message)
        
        return JsonResponse({
            'message': assistant_message
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
