from django.urls import path
from . import views

app_name = 'intellichat'

urlpatterns = [
    path('', views.intellichat, name='intellichat'),
    path('message/', views.chat_message, name='message'),
    path('conversation/<int:conversation_id>/', views.get_conversation, name='get_conversation'),
    path('conversation/<int:conversation_id>/delete/', views.delete_conversation, name='delete_conversation'),
    path('history/', views.chat_history, name='chat_history'),
] 