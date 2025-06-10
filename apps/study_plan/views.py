from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import StudyTask, StudyGoal, StudyPlan
from django.http import JsonResponse, FileResponse
from django.views.decorators.http import require_http_methods
from .llm_utils import generate_study_plan, get_chat_response
import json
import traceback
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListItem, ListFlowable
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
import re
from django.db.models import Case, When

# Import the custom template filter
from .templatetags.plan_format import format_study_plan

# Create your views here.

@login_required
def study_plan(request):
    tasks = StudyTask.objects.filter(user=request.user)
    goals = StudyGoal.objects.filter(user=request.user)
    plans = StudyPlan.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'study_plan/index.html', {
        'tasks': tasks,
        'goals': goals,
        'plans': plans,
    })

@login_required
@require_http_methods(['POST'])
def create_task(request):
    data = json.loads(request.body)
    task = StudyTask.objects.create(
        user=request.user,
        title=data.get('title'),
        description=data.get('description', ''),
        priority=data.get('priority', 'medium').lower(),
        status=data.get('status', 'not_started').lower(),
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
        notes = data.get('notes', '').strip()
        
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
        valid_levels = ['beginner', 'intermediate', 'advanced', 'expert']
        if level not in valid_levels:
            level = 'intermediate'  # Default to intermediate if invalid
        
        print(f"Generating plan - Subject: {subject}, Days: {days}, Hours: {hours}, Level: {level}")
        
        # Generate study plan using Gemini model
        plan = generate_study_plan(subject, days, hours, level)
        
        # Check if the response contains an error message
        if plan.startswith('Error'):
            print(f"Error in plan generation: {plan}")
            return JsonResponse({'error': plan}, status=500)
        
        # Save the generated plan to the database
        new_plan = StudyPlan.objects.create(
            user=request.user,
            subject=subject,
            days=days,
            hours=hours,
            level=level,
            notes=notes,
            plan_text=plan
        )
        
        print(f"Successfully generated plan: {plan[:100]}...")

        # Apply the formatting filter
        formatted_plan_html = format_study_plan(plan)

        return JsonResponse({
            'plan': formatted_plan_html,
            'id': new_plan.id,
            'subject': new_plan.subject,
            'days': new_plan.days,
            'hours': new_plan.hours,
            'level': new_plan.level,
            'notes': new_plan.notes,
            'created_at': new_plan.created_at.strftime('%b %d, %Y %H:%M')
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

@login_required
@require_http_methods(['POST'])
def download_study_plan_pdf(request):
    try:
        data = json.loads(request.body)
        plan_content = data.get('plan')
        
        if not plan_content:
            return JsonResponse({'error': 'Plan content is required'}, status=400)

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
            title="Study Plan"
        )
        styles = getSampleStyleSheet()
        # Modern, web-like styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=26,
            spaceAfter=32,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#6366f1'),
            fontName='Helvetica-Bold',
        )
        h2_style = ParagraphStyle(
            'H2',
            parent=styles['Heading2'],
            fontSize=20,
            spaceBefore=18,
            spaceAfter=10,
            textColor=colors.HexColor('#4338ca'),
            fontName='Helvetica-Bold',
        )
        h3_style = ParagraphStyle(
            'H3',
            parent=styles['Heading3'],
            fontSize=16,
            spaceBefore=14,
            spaceAfter=8,
            textColor=colors.HexColor('#6366f1'),
            fontName='Helvetica-Bold',
        )
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=10,
            textColor=colors.HexColor('#374151'),
            fontName='Helvetica',
            leading=18,
        )
        bullet_style = ParagraphStyle(
            'BulletPoint',
            parent=normal_style,
            leftIndent=24,
            bulletIndent=12,
            spaceBefore=2,
            spaceAfter=2,
        )
        numbered_style = ParagraphStyle(
            'NumberedPoint',
            parent=normal_style,
            leftIndent=24,
            bulletIndent=12,
            spaceBefore=2,
            spaceAfter=2,
        )
        elements = []
        elements.append(Spacer(1, 16))
        elements.append(Paragraph("Study Plan", title_style))
        elements.append(Spacer(1, 24))
        lines = plan_content.split('\n')
        in_ul = False
        in_ol = False
        current_list_items = []
        for line in lines:
            stripped = line.strip()
            stripped = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', stripped)
            # Headings
            if re.match(r'^#{1,2} ', stripped):
                if in_ul and current_list_items:
                    elements.append(ListFlowable(current_list_items, bulletType='bullet', start='•', style=bullet_style))
                    elements.append(Spacer(1, 8))
                    current_list_items = []
                    in_ul = False
                if in_ol and current_list_items:
                    elements.append(ListFlowable(current_list_items, bulletType='1', style=numbered_style))
                    elements.append(Spacer(1, 8))
                    current_list_items = []
                    in_ol = False
                level = 2 if stripped.startswith('##') else 3
                heading = re.sub(r'^#{1,2} ', '', stripped)
                style = h2_style if level == 2 else h3_style
                elements.append(Spacer(1, 10))
                elements.append(Paragraph(heading, style))
                elements.append(Spacer(1, 4))
                continue
            elif re.match(r'^[A-Z0-9\s]{4,}:?$', stripped) and not re.match(r'^\d+\. ', stripped):
                if in_ul and current_list_items:
                    elements.append(ListFlowable(current_list_items, bulletType='bullet', start='•', style=bullet_style))
                    elements.append(Spacer(1, 8))
                    current_list_items = []
                    in_ul = False
                if in_ol and current_list_items:
                    elements.append(ListFlowable(current_list_items, bulletType='1', style=numbered_style))
                    elements.append(Spacer(1, 8))
                    current_list_items = []
                    in_ol = False
                heading = stripped.rstrip(':')
                elements.append(Spacer(1, 10))
                elements.append(Paragraph(heading.title(), h3_style))
                elements.append(Spacer(1, 4))
                continue
            # Unordered list
            if stripped.startswith('* ') or stripped.startswith('- '):
                if in_ol and current_list_items:
                    elements.append(ListFlowable(current_list_items, bulletType='1', style=numbered_style))
                    elements.append(Spacer(1, 8))
                    current_list_items = []
                    in_ol = False
                if not in_ul:
                    in_ul = True
                current_list_items.append(ListItem(Paragraph(stripped[2:].strip(), bullet_style)))
                continue
            # Ordered list
            if re.match(r'^\d+\. ', stripped):
                if in_ul and current_list_items:
                    elements.append(ListFlowable(current_list_items, bulletType='bullet', start='•', style=bullet_style))
                    elements.append(Spacer(1, 8))
                    current_list_items = []
                    in_ul = False
                if not in_ol:
                    in_ol = True
                current_list_items.append(ListItem(Paragraph(re.sub(r"^\d+\. ", "", stripped), numbered_style)))
                continue
            # Paragraph
            if stripped:
                if in_ul and current_list_items:
                    elements.append(ListFlowable(current_list_items, bulletType='bullet', start='•', style=bullet_style))
                    elements.append(Spacer(1, 8))
                    current_list_items = []
                    in_ul = False
                if in_ol and current_list_items:
                    elements.append(ListFlowable(current_list_items, bulletType='1', style=numbered_style))
                    elements.append(Spacer(1, 8))
                    current_list_items = []
                    in_ol = False
                elements.append(Paragraph(stripped, normal_style))
                elements.append(Spacer(1, 2))
        if in_ul and current_list_items:
            elements.append(ListFlowable(current_list_items, bulletType='bullet', start='•', style=bullet_style))
            elements.append(Spacer(1, 8))
        if in_ol and current_list_items:
            elements.append(ListFlowable(current_list_items, bulletType='1', style=numbered_style))
            elements.append(Spacer(1, 8))
        doc.build(elements)
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='study_plan.pdf', content_type='application/pdf')
    except Exception as e:
        print(f"Unexpected error in download_study_plan_pdf: {str(e)}")
        print("Full traceback:")
        print(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def view_study_plan(request, plan_id):
    plan = get_object_or_404(StudyPlan, id=plan_id, user=request.user)
    return render(request, 'study_plan/plan_detail.html', {'plan': plan})

@login_required
@require_http_methods(['DELETE'])
def delete_study_plan(request, plan_id):
    plan = get_object_or_404(StudyPlan, id=plan_id, user=request.user)
    plan.delete()
    return JsonResponse({'success': True})

@login_required
def view_tasks(request):
    tasks = StudyTask.objects.filter(user=request.user)

    # Get filter parameters from request
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    search_query = request.GET.get('search')

    # Apply filters
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    if search_query:
        tasks = tasks.filter(title__icontains=search_query)

    # Apply sorting
    tasks = tasks.order_by(
        Case(
            When(priority='high', then=0),
            When(priority='medium', then=1),
            When(priority='low', then=2),
            default=3,
        ),
        Case(
            When(status='not_started', then=0),
            When(status='in_progress', then=1),
            When(status='completed', then=2),
            default=3,
        ),
        '-created_at'
    )

    # Check if the request is AJAX
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        # If it's an AJAX request, render only the task list snippet
        return render(request, 'study_plan/_task_list.html', {
            'tasks': tasks,
        })
    else:
        # If it's a regular request, render the full page
        return render(request, 'study_plan/tasks.html', {
            'tasks': tasks,
        })
