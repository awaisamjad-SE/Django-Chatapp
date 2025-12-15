from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db.models import Q
from .models import Message
from django.http import JsonResponse
from django.utils import timezone


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('user_list')
    else:
        form = UserCreationForm()
    return render(request, 'chat/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('user_list')
    else:
        form = AuthenticationForm()
    return render(request, 'chat/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('login')


@login_required
def user_list(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'chat/user_list.html', {'users': users})


@login_required
def chat_room(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    messages = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).order_by('timestamp')
    
    # Mark received messages as delivered and read
    unread_messages = Message.objects.filter(sender=other_user, receiver=request.user, status='sent')
    unread_messages.update(status='delivered', delivered_at=timezone.now())
    
    Message.objects.filter(
        sender=other_user, 
        receiver=request.user, 
        is_read=False
    ).update(is_read=True, status='read', read_at=timezone.now())
    
    if request.method == 'POST':
        content = request.POST.get('content')
        image = request.FILES.get('image')
        file = request.FILES.get('file')
        
        if content or image or file:
            msg = Message.objects.create(
                sender=request.user,
                receiver=other_user,
                content=content if content else '',
                image=image,
                file=file,
                file_name=file.name if file else None,
                status='sent'
            )
            return redirect('chat_room', user_id=user_id)
    
    return render(request, 'chat/chat_room.html', {
        'other_user': other_user,
        'messages': messages
    })


@login_required
def get_messages(request, user_id):
    """API endpoint to fetch new messages"""
    other_user = get_object_or_404(User, id=user_id)
    messages = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).order_by('timestamp')
    
    # Mark received messages as delivered
    undelivered = Message.objects.filter(sender=other_user, receiver=request.user, status='sent')
    undelivered.update(status='delivered', delivered_at=timezone.now())
    
    # Mark received messages as read
    unread = Message.objects.filter(sender=other_user, receiver=request.user, is_read=False)
    unread.update(is_read=True, status='read', read_at=timezone.now())
    
    messages_data = [{
        'id': msg.id,
        'sender': msg.sender.username,
        'content': msg.content,
        'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'is_sender': msg.sender == request.user,
        'status': msg.status,
        'image': msg.image.url if msg.image else None,
        'file': msg.file.url if msg.file else None,
        'file_name': msg.file_name
    } for msg in messages]
    
    return JsonResponse({'messages': messages_data})


@login_required
def update_message_status(request, message_id):
    """Update message status when viewed"""
    message = get_object_or_404(Message, id=message_id, receiver=request.user)
    
    if message.status == 'sent':
        message.status = 'delivered'
        message.delivered_at = timezone.now()
    elif message.status == 'delivered':
        message.status = 'read'
        message.read_at = timezone.now()
        message.is_read = True
    
    message.save()
    return JsonResponse({'status': message.status})


@login_required
def check_new_messages(request):
    """Check for new messages for notifications"""
    unread_messages = Message.objects.filter(
        receiver=request.user,
        is_read=False
    ).select_related('sender').order_by('-timestamp')
    
    notifications = [{
        'id': msg.id,
        'sender': msg.sender.username,
        'sender_id': msg.sender.id,
        'content': msg.content[:50] if msg.content else 'Sent a file',
        'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'has_image': bool(msg.image),
        'has_file': bool(msg.file)
    } for msg in unread_messages[:5]]  # Last 5 unread
    
    return JsonResponse({
        'notifications': notifications,
        'count': unread_messages.count()
    })
