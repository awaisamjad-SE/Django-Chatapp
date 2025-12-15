from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_list, name='user_list'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('chat/<int:user_id>/', views.chat_room, name='chat_room'),
    path('api/messages/<int:user_id>/', views.get_messages, name='get_messages'),
    path('api/message/<int:message_id>/status/', views.update_message_status, name='update_message_status'),
    path('api/notifications/', views.check_new_messages, name='check_new_messages'),
]
