from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.study_plan.models import StudyTask, StudyGoal
from django.utils import timezone
from django.db.models import Count
from datetime import timedelta
from django.http import JsonResponse

@login_required
def dashboard(request):
    # Get recent tasks and goals
    recent_tasks = StudyTask.objects.filter(user=request.user).order_by('-created_at')[:5]
    upcoming_tasks = StudyTask.objects.filter(
        user=request.user,
        status__in=['not_started', 'in_progress']
    ).order_by('due_date')[:5]
    total_pending_tasks_count = StudyTask.objects.filter(
        user=request.user,
        status__in=['not_started', 'in_progress']
    ).count()
    recent_goals = StudyGoal.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    # Get weekly statistics
    week_start = timezone.now().date() - timedelta(days=timezone.now().date().weekday())
    week_end = week_start + timedelta(days=6)
    
    # Get all tasks for the current week
    weekly_tasks = StudyTask.objects.filter(
        user=request.user,
        created_at__date__gte=week_start,
        created_at__date__lte=week_end
    )
    
    # Calculate statistics
    completed_tasks_count = weekly_tasks.filter(status='completed').count()
    total_tasks_count = weekly_tasks.count()
    high_priority_count = weekly_tasks.filter(priority='high').count()
    
    # Calculate completion rate
    completion_rate = 0
    if total_tasks_count > 0:
        completion_rate = round((completed_tasks_count / total_tasks_count) * 100)
    
    # Get most common subject (if you have a subject field in your tasks)
    most_common_subject = None
    if hasattr(StudyTask, 'subject'):
        most_common_subject = weekly_tasks.values('subject').annotate(
            count=Count('subject')
        ).order_by('-count').first()
        if most_common_subject:
            most_common_subject = most_common_subject['subject']
    
    context = {
        'recent_tasks': recent_tasks,
        'upcoming_tasks': upcoming_tasks,
        'total_pending_tasks_count': total_pending_tasks_count,
        'recent_goals': recent_goals,
        'completed_tasks_count': completed_tasks_count,
        'total_tasks_count': total_tasks_count,
        'high_priority_count': high_priority_count,
        'completion_rate': completion_rate,
        'most_common_subject': most_common_subject,
        'now': timezone.now(),
    }
    
    # Check if the request is AJAX and which part is requested
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    requested_card = request.GET.get('card')
    
    if is_ajax:
        if requested_card == 'study_plan':
            # Render only the study plan card
            return render(request, 'dashboard/_study_plan_card.html', context)
        elif requested_card == 'weekly_progress':
            # Render only the weekly progress card
            return render(request, 'dashboard/_progress_card.html', context)
        else:
            # Default AJAX response (can be customized)
            return JsonResponse({'status': 'success', 'message': 'AJAX request received'})
    else:
        # If it's a regular request, render the full page
        return render(request, 'dashboard/index.html', context)
