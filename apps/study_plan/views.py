from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import StudyTask, StudyGoal
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .llm_utils import generate_study_plan, get_chat_response
import json
import traceback

# Create your views here.

@login_required
def study_plan(request):
    tasks = StudyTask.objects.filter(user=request.user)
    goals = StudyGoal.objects.filter(user=request.user)
    return render(request, 'study_plan/index.html', {
        'tasks': tasks,
        'goals': goals
    })

@login_required
@require_http_methods(['POST'])
def create_task(request):
    data = json.loads(request.body)
    task = StudyTask.objects.create(
        user=request.user,
        title=data.get('title'),
        description=data.get('description', ''),
        priority=data.get('priority', 'medium'),
        due_date=data.get('due_date')
    )
    return JsonResponse({
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'priority': task.priority,
        'status': task.status,
        'due_date': task.due_date
    })

@login_required
@require_http_methods(['PUT'])
def update_task(request, task_id):
    task = get_object_or_404(StudyTask, id=task_id, user=request.user)
    data = json.loads(request.body)
    
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.priority = data.get('priority', task.priority)
    task.status = data.get('status', task.status)
    task.due_date = data.get('due_date', task.due_date)
    task.save()
    
    return JsonResponse({
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'priority': task.priority,
        'status': task.status,
        'due_date': task.due_date
    })

@login_required
@require_http_methods(['DELETE'])
def delete_task(request, task_id):
    task = get_object_or_404(StudyTask, id=task_id, user=request.user)
    task.delete()
    return JsonResponse({'status': 'success'})

@login_required
@require_http_methods(['POST'])
def create_goal(request):
    data = json.loads(request.body)
    goal = StudyGoal.objects.create(
        user=request.user,
        title=data.get('title'),
        description=data.get('description', ''),
        target_date=data.get('target_date')
    )
    return JsonResponse({
        'id': goal.id,
        'title': goal.title,
        'description': goal.description,
        'target_date': goal.target_date,
        'is_achieved': goal.is_achieved
    })

@login_required
@require_http_methods(['PUT'])
def update_goal(request, goal_id):
    goal = get_object_or_404(StudyGoal, id=goal_id, user=request.user)
    data = json.loads(request.body)
    
    goal.title = data.get('title', goal.title)
    goal.description = data.get('description', goal.description)
    goal.target_date = data.get('target_date', goal.target_date)
    goal.is_achieved = data.get('is_achieved', goal.is_achieved)
    goal.save()
    
    return JsonResponse({
        'id': goal.id,
        'title': goal.title,
        'description': goal.description,
        'target_date': goal.target_date,
        'is_achieved': goal.is_achieved
    })

@login_required
@require_http_methods(['DELETE'])
def delete_goal(request, goal_id):
    goal = get_object_or_404(StudyGoal, id=goal_id, user=request.user)
    goal.delete()
    return JsonResponse({'status': 'success'})

@login_required
@require_http_methods(['POST'])
def generate_ai_study_plan(request):
    try:
        print("Received study plan generation request")
        data = json.loads(request.body)
        
        # Extract and validate parameters
        subject = data.get('subject', '').strip()
        days = data.get('days', 7)
        hours = data.get('hours', 2)
        level = data.get('level', 'intermediate').lower()
        
        # Validate required fields
        if not subject:
            return JsonResponse({'error': 'Subject is required'}, status=400)
            
        # Validate numeric fields
        try:
            days = int(days)
            hours = float(hours)
            if days < 1 or hours < 0.5:
                return JsonResponse({'error': 'Invalid days or hours value'}, status=400)
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Days and hours must be valid numbers'}, status=400)
            
        # Validate level
        valid_levels = ['beginner', 'intermediate', 'expert']
        if level not in valid_levels:
            level = 'intermediate'  # Default to intermediate if invalid
        
        print(f"Generating plan - Subject: {subject}, Days: {days}, Hours: {hours}, Level: {level}")
        
        # Generate study plan using Gemini model
        plan = generate_study_plan(subject, days, hours, level)
        
        # Check if the response contains an error message
        if plan.startswith('Error'):
            print(f"Error in plan generation: {plan}")
            return JsonResponse({'error': plan}, status=500)
        
        print(f"Successfully generated plan: {plan[:100]}...")
        return JsonResponse({
            'plan': plan
        })
        
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON format: {str(e)}"
        print(error_msg)
        return JsonResponse({'error': error_msg}, status=400)
    except Exception as e:
        error_msg = f"Unexpected error in generate_ai_study_plan: {str(e)}"
        print(error_msg)
        print("Full traceback:")
        print(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(['POST'])
def send_chat_message(request):
    try:
        print("Received chat message request")
        data = json.loads(request.body)
        message = data.get('message')
        
        if not message:
            print("Error: Empty message received")
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        print(f"Processing message: {message[:100]}...")  # Log first 100 chars
        
        # Get chat response using Gemini model
        try:
            response = get_chat_response(message)
            print(f"Got response from LLM: {response[:100]}...")  # Log first 100 chars
            
            if response.startswith('Error'):
                print(f"LLM returned error: {response}")
                return JsonResponse({'error': response}, status=500)
            
            return JsonResponse({
                'response': response
            })
            
        except Exception as e:
            print(f"Error in LLM processing: {str(e)}")
            return JsonResponse({'error': f"Error processing message: {str(e)}"}, status=500)
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {str(e)}")
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    except Exception as e:
        print(f"Unexpected error in send_chat_message: {str(e)}")
        import traceback
        print("Full traceback:")
        print(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)
