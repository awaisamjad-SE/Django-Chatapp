from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db.models import Q
from .models import Message, Friendship, BlockedUser
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages


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
    # Get all users except current user
    all_users = User.objects.exclude(id=request.user.id)
    
    # Get blocked users
    blocked_user_ids = BlockedUser.objects.filter(blocker=request.user).values_list('blocked_id', flat=True)
    blocked_by_ids = BlockedUser.objects.filter(blocked=request.user).values_list('blocker_id', flat=True)
    
    # Get friends (accepted friendships)
    friend_ids = Friendship.objects.filter(
        Q(from_user=request.user, status='accepted') |
        Q(to_user=request.user, status='accepted')
    ).values_list('from_user_id', 'to_user_id')
    
    friend_id_list = set()
    for from_id, to_id in friend_ids:
        friend_id_list.add(from_id if from_id != request.user.id else to_id)
    
    # Get pending requests sent by current user
    sent_request_ids = Friendship.objects.filter(
        from_user=request.user, status='pending'
    ).values_list('to_user_id', flat=True)
    
    # Get pending requests received by current user
    received_request_ids = Friendship.objects.filter(
        to_user=request.user, status='pending'
    ).values_list('from_user_id', flat=True)
    
    # Categorize users
    users_data = []
    for user in all_users:
        if user.id in blocked_user_ids or user.id in blocked_by_ids:
            status = 'blocked'
        elif user.id in friend_id_list:
            status = 'friend'
        elif user.id in sent_request_ids:
            status = 'request_sent'
        elif user.id in received_request_ids:
            status = 'request_received'
        else:
            status = 'none'
        
        users_data.append({
            'user': user,
            'status': status
        })
    
    return render(request, 'chat/user_list.html', {'users_data': users_data})


@login_required
def chat_room(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    
    # Check if users are friends
    are_friends = Friendship.objects.filter(
        Q(from_user=request.user, to_user=other_user, status='accepted') |
        Q(from_user=other_user, to_user=request.user, status='accepted')
    ).exists()
    
    # Check if blocked
    is_blocked = BlockedUser.objects.filter(
        Q(blocker=request.user, blocked=other_user) |
        Q(blocker=other_user, blocked=request.user)
    ).exists()
    
    if not are_friends or is_blocked:
        messages.error(request, 'You can only chat with your friends.')
        return redirect('user_list')
    
    message_list = Message.objects.filter(
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
        'messages': message_list
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


# Friend Management Views

@login_required
def send_friend_request(request):
    """Send friend request by username or email"""
    if request.method == 'POST':
        identifier = request.POST.get('identifier', '').strip()
        
        if not identifier:
            messages.error(request, 'Please enter a username or email.')
            return redirect('user_list')
        
        # Try to find user by username or email
        try:
            if '@' in identifier:
                to_user = User.objects.get(email=identifier)
            else:
                to_user = User.objects.get(username=identifier)
        except User.DoesNotExist:
            messages.error(request, f'User "{identifier}" not found.')
            return redirect('user_list')
        
        if to_user == request.user:
            messages.error(request, 'You cannot send a friend request to yourself.')
            return redirect('user_list')
        
        # Check if blocked
        if BlockedUser.objects.filter(
            Q(blocker=request.user, blocked=to_user) |
            Q(blocker=to_user, blocked=request.user)
        ).exists():
            messages.error(request, 'Cannot send friend request to this user.')
            return redirect('user_list')
        
        # Check if already friends
        if Friendship.objects.filter(
            Q(from_user=request.user, to_user=to_user, status='accepted') |
            Q(from_user=to_user, to_user=request.user, status='accepted')
        ).exists():
            messages.info(request, f'You are already friends with {to_user.username}.')
            return redirect('user_list')
        
        # Check if request already exists
        existing_request = Friendship.objects.filter(
            Q(from_user=request.user, to_user=to_user) |
            Q(from_user=to_user, to_user=request.user)
        ).first()
        
        if existing_request:
            if existing_request.status == 'pending':
                if existing_request.from_user == request.user:
                    messages.info(request, 'Friend request already sent.')
                else:
                    messages.info(request, 'This user has already sent you a friend request. Check your pending requests.')
            elif existing_request.status == 'rejected':
                # Update to pending again
                existing_request.status = 'pending'
                existing_request.from_user = request.user
                existing_request.to_user = to_user
                existing_request.save()
                messages.success(request, f'Friend request sent to {to_user.username}.')
        else:
            # Create new request
            Friendship.objects.create(from_user=request.user, to_user=to_user)
            messages.success(request, f'Friend request sent to {to_user.username}.')
        
        return redirect('user_list')
    
    return redirect('user_list')


@login_required
def accept_friend_request(request, request_id):
    """Accept a friend request"""
    friend_request = get_object_or_404(Friendship, id=request_id, to_user=request.user, status='pending')
    friend_request.status = 'accepted'
    friend_request.save()
    messages.success(request, f'You are now friends with {friend_request.from_user.username}.')
    return redirect('friend_requests')


@login_required
def reject_friend_request(request, request_id):
    """Reject a friend request"""
    friend_request = get_object_or_404(Friendship, id=request_id, to_user=request.user, status='pending')
    friend_request.status = 'rejected'
    friend_request.save()
    messages.info(request, f'Friend request from {friend_request.from_user.username} rejected.')
    return redirect('friend_requests')


@login_required
def cancel_friend_request(request, user_id):
    """Cancel a sent friend request"""
    to_user = get_object_or_404(User, id=user_id)
    friend_request = get_object_or_404(Friendship, from_user=request.user, to_user=to_user, status='pending')
    friend_request.delete()
    messages.info(request, f'Friend request to {to_user.username} cancelled.')
    return redirect('user_list')


@login_required
def unfriend_user(request, user_id):
    """Remove a friend"""
    other_user = get_object_or_404(User, id=user_id)
    friendship = Friendship.objects.filter(
        Q(from_user=request.user, to_user=other_user, status='accepted') |
        Q(from_user=other_user, to_user=request.user, status='accepted')
    ).first()
    
    if friendship:
        friendship.delete()
        messages.success(request, f'You are no longer friends with {other_user.username}.')
    
    return redirect('friends_list')


@login_required
def friends_list(request):
    """View all friends"""
    # Get accepted friendships
    friendships = Friendship.objects.filter(
        Q(from_user=request.user, status='accepted') |
        Q(to_user=request.user, status='accepted')
    )
    
    friends = []
    for friendship in friendships:
        friend = friendship.to_user if friendship.from_user == request.user else friendship.from_user
        friends.append({
            'user': friend,
            'friendship_id': friendship.id,
            'since': friendship.updated_at
        })
    
    return render(request, 'chat/friends_list.html', {'friends': friends})


@login_required
def friend_requests(request):
    """View received friend requests"""
    received_requests = Friendship.objects.filter(
        to_user=request.user,
        status='pending'
    ).select_related('from_user')
    
    sent_requests = Friendship.objects.filter(
        from_user=request.user,
        status='pending'
    ).select_related('to_user')
    
    return render(request, 'chat/friend_requests.html', {
        'received_requests': received_requests,
        'sent_requests': sent_requests
    })


@login_required
def block_user(request, user_id):
    """Block a user"""
    user_to_block = get_object_or_404(User, id=user_id)
    
    if user_to_block == request.user:
        messages.error(request, 'You cannot block yourself.')
        return redirect('user_list')
    
    # Remove friendship if exists
    Friendship.objects.filter(
        Q(from_user=request.user, to_user=user_to_block) |
        Q(from_user=user_to_block, to_user=request.user)
    ).delete()
    
    # Create block
    BlockedUser.objects.get_or_create(blocker=request.user, blocked=user_to_block)
    messages.success(request, f'{user_to_block.username} has been blocked.')
    
    return redirect('blocked_users')


@login_required
def unblock_user(request, user_id):
    """Unblock a user"""
    user_to_unblock = get_object_or_404(User, id=user_id)
    blocked = BlockedUser.objects.filter(blocker=request.user, blocked=user_to_unblock)
    
    if blocked.exists():
        blocked.delete()
        messages.success(request, f'{user_to_unblock.username} has been unblocked.')
    
    return redirect('blocked_users')


@login_required
def blocked_users(request):
    """View all blocked users"""
    blocked = BlockedUser.objects.filter(blocker=request.user).select_related('blocked')
    return render(request, 'chat/blocked_users.html', {'blocked_users': blocked})


@login_required
def search_users(request):
    """Search users by username or email for friend requests"""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return render(request, 'chat/search_users.html', {'users': []})
    
    # Search by username or email
    users = User.objects.filter(
        Q(username__icontains=query) | Q(email__icontains=query)
    ).exclude(id=request.user.id)[:10]  # Limit to 10 results
    
    # Get blocked users
    blocked_user_ids = BlockedUser.objects.filter(blocker=request.user).values_list('blocked_id', flat=True)
    
    # Get friend status for each user
    users_data = []
    for user in users:
        if user.id in blocked_user_ids:
            continue
            
        # Check friendship status
        friendship = Friendship.objects.filter(
            Q(from_user=request.user, to_user=user) |
            Q(from_user=user, to_user=request.user)
        ).first()
        
        status = 'none'
        if friendship:
            if friendship.status == 'accepted':
                status = 'friend'
            elif friendship.status == 'pending':
                status = 'request_sent' if friendship.from_user == request.user else 'request_received'
        
        users_data.append({
            'user': user,
            'status': status
        })
    
    return render(request, 'chat/search_users.html', {'users': users_data, 'query': query})
