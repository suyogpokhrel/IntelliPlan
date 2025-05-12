from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.study_plan.models import StudyTask, StudyGoal
from django.utils import timezone

@login_required
def dashboard(request):
    # Get recent tasks and goals
    recent_tasks = StudyTask.objects.filter(user=request.user).order_by('-created_at')[:5]
    upcoming_tasks = StudyTask.objects.filter(
        user=request.user,
        status__in=['not_started', 'in_progress']
    ).order_by('due_date')[:5]
    recent_goals = StudyGoal.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    # Get statistics
    completed_tasks_count = StudyTask.objects.filter(
        user=request.user,
        status='completed'
    ).count()
    
    achieved_goals_count = StudyGoal.objects.filter(
        user=request.user,
        is_achieved=True
    ).count()
    
    context = {
        'recent_tasks': recent_tasks,
        'upcoming_tasks': upcoming_tasks,
        'recent_goals': recent_goals,
        'completed_tasks_count': completed_tasks_count,
        'achieved_goals_count': achieved_goals_count,
        'now': timezone.now(),
    }
    
    return render(request, 'dashboard/index.html', context)
