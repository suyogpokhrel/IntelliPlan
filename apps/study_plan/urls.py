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
] 