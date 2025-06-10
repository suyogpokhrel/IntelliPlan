from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from apps.study_plan.llm_utils import get_chat_response
from .models import ChatConversation, ChatMessage
import json

@login_required
def intellichat(request):
    conversations = ChatConversation.objects.filter(user=request.user)
    return render(request, 'intellichat/index.html', {
        'conversations': conversations
    })

@login_required
@require_http_methods(['POST'])
def chat_message(request):
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        conversation_id = data.get('conversation_id')
        
        if not user_message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        # Get or create conversation
        if conversation_id:
            conversation = get_object_or_404(ChatConversation, id=conversation_id, user=request.user)
        else:
            # Create new conversation with first message as title
            title = user_message[:50] + ('...' if len(user_message) > 50 else '')
            conversation = ChatConversation.objects.create(
                user=request.user,
                title=title
            )
        
        # Save user message
        ChatMessage.objects.create(
            conversation=conversation,
            content=user_message,
            is_user=True
        )
        
        # Get response using Gemini model
        assistant_message = get_chat_response(user_message)
        
        # Save assistant message
        ChatMessage.objects.create(
            conversation=conversation,
            content=assistant_message,
            is_user=False
        )
        
        return JsonResponse({
            'message': assistant_message,
            'conversation_id': conversation.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(['GET'])
def get_conversation(request, conversation_id):
    conversation = get_object_or_404(ChatConversation, id=conversation_id, user=request.user)
    messages = conversation.messages.all()
    
    return JsonResponse({
        'conversation': {
            'id': conversation.id,
            'title': conversation.title,
            'messages': [
                {
                    'content': msg.content,
                    'is_user': msg.is_user,
                    'timestamp': msg.timestamp.strftime('%I:%M %p')
                }
                for msg in messages
            ]
        }
    })

@login_required
@require_http_methods(['DELETE'])
def delete_conversation(request, conversation_id):
    conversation = get_object_or_404(ChatConversation, id=conversation_id, user=request.user)
    conversation.delete()
    return JsonResponse({'status': 'success'})

@login_required
def chat_history(request):
    conversations = ChatConversation.objects.filter(user=request.user)
    return render(request, 'intellichat/history.html', {
        'conversations': conversations
    })
