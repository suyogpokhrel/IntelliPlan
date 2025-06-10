from django.urls import path
from . import views

app_name = 'study_plan'

urlpatterns = [
    path('', views.study_plan, name='study_plan'),
    path('tasks/create/', views.create_task, name='create_task'),
    path('tasks/<int:task_id>/update/', views.update_task, name='update_task'),
    path('tasks/<int:task_id>/delete/', views.delete_task, name='delete_task'),
    path('goals/create/', views.create_goal, name='create_goal'),
    path('goals/<int:goal_id>/update/', views.update_goal, name='update_goal'),
    path('goals/<int:goal_id>/delete/', views.delete_goal, name='delete_goal'),
    path('generate-plan/', views.generate_ai_study_plan, name='generate_ai_study_plan'),
    path('send-message/', views.send_chat_message, name='send_chat_message'),
    path('download-pdf/', views.download_study_plan_pdf, name='download_study_plan_pdf'),
    path('plans/<int:plan_id>/', views.view_study_plan, name='view_study_plan'),
    path('plans/<int:plan_id>/delete/', views.delete_study_plan, name='delete_study_plan'),
    path('tasks/all/', views.view_tasks, name='view_tasks'),
] 