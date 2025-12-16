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
    
    # Friend Management URLs
    path('friends/', views.friends_list, name='friends_list'),
    path('friend-requests/', views.friend_requests, name='friend_requests'),
    path('send-friend-request/', views.send_friend_request, name='send_friend_request'),
    path('accept-request/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('reject-request/<int:request_id>/', views.reject_friend_request, name='reject_friend_request'),
    path('cancel-request/<int:user_id>/', views.cancel_friend_request, name='cancel_friend_request'),
    path('unfriend/<int:user_id>/', views.unfriend_user, name='unfriend_user'),
    path('block/<int:user_id>/', views.block_user, name='block_user'),
    path('unblock/<int:user_id>/', views.unblock_user, name='unblock_user'),
    path('blocked-users/', views.blocked_users, name='blocked_users'),
    path('search-users/', views.search_users, name='search_users'),
]
