from django.contrib import admin
from .models import Message


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
