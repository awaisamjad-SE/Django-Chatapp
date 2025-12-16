from django.contrib import admin
from .models import Message, Friendship, BlockedUser


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'content_preview', 'status', 'timestamp', 'is_read']
    list_filter = ['status', 'is_read', 'timestamp']
    search_fields = ['sender__username', 'receiver__username', 'content']
    readonly_fields = ['timestamp', 'delivered_at', 'read_at']
    
    def content_preview(self, obj):
        if obj.content:
            return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
        elif obj.image:
            return '[Image]'
        elif obj.file:
            return f'[File: {obj.file_name}]'
        return '[Empty]'
    
    content_preview.short_description = 'Content'


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ['from_user', 'to_user', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at']
    search_fields = ['from_user__username', 'to_user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('from_user', 'to_user')


@admin.register(BlockedUser)
class BlockedUserAdmin(admin.ModelAdmin):
    list_display = ['blocker', 'blocked', 'blocked_at']
    list_filter = ['blocked_at']
    search_fields = ['blocker__username', 'blocked__username']
    readonly_fields = ['blocked_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('blocker', 'blocked')
