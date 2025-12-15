# Django Chat Application

A real-time chat application built with Django where two users can communicate with each other.

## Features

- User registration and authentication
- Real-time messaging between users
- User list to select chat partners
- Message history
- Auto-refresh messages every 2 seconds
- Clean and modern UI with gradient design
- Message timestamps
- Read/unread message tracking

## Installation & Setup

### 1. Navigate to the project directory
```bash
cd "c:\Users\Black box\OneDrive\Documents\GitHub\Chatapp\Chatapp"
```

### 2. Create and apply migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create a superuser (optional, for admin access)
```bash
python manage.py createsuperuser
```

### 4. Run the development server
```bash
python manage.py runserver
```

### 5. Open your browser and visit
```
http://127.0.0.1:8000/
```

## How to Use

1. **Register**: Create two user accounts (open two different browsers or use incognito mode)
   - Go to the registration page
   - Create first user account (e.g., "user1")
   - Logout and create second user account (e.g., "user2")

2. **Login**: Login with one of the accounts

3. **Select User**: From the user list, click on the user you want to chat with

4. **Chat**: 
   - Type your message in the input field
   - Click "Send" or press Enter
   - Messages will appear in real-time
   - The chat automatically refreshes every 2 seconds to fetch new messages

5. **Testing Real-time Chat**:
   - Open two browser windows/tabs
   - Login with different users in each
   - Start a conversation and watch messages appear in real-time!

## Project Structure

```
Chatapp/
├── manage.py
├── Chatapp/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
└── chat/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py          # Message model
    ├── views.py           # Chat views and logic
    ├── urls.py            # URL routing
    ├── templates/
    │   └── chat/
    │       ├── base.html       # Base template
    │       ├── register.html   # Registration page
    │       ├── login.html      # Login page
    │       ├── user_list.html  # User selection
    │       └── chat_room.html  # Chat interface
    └── migrations/
```

## Features Explained

### Models
- **Message Model**: Stores messages with sender, receiver, content, timestamp, and read status

### Views
- **register**: User registration
- **user_login**: User authentication
- **user_list**: Display all available users to chat with
- **chat_room**: Main chat interface with message display and sending
- **get_messages**: API endpoint for fetching messages (used for auto-refresh)

### Auto-refresh
- Messages are fetched every 2 seconds using JavaScript
- No page reload needed
- Smooth animation when new messages arrive

## Future Enhancements

To add WebSocket support for true real-time messaging (optional):
1. Install Django Channels: `pip install channels channels-redis`
2. Configure ASGI and WebSocket consumers
3. Set up Redis for channel layers

For now, the polling mechanism (auto-refresh every 2 seconds) provides a good user experience for real-time-like chatting.

## Technologies Used

- Django 5.2.8
- SQLite (default database)
- HTML/CSS
- JavaScript (for auto-refresh)
- Python 3.x

## Notes

- The application uses Django's built-in authentication system
- Messages are stored in SQLite database
- The UI uses CSS gradients and modern design principles
- Auto-refresh polling is set to 2 seconds (adjustable in chat_room.html)

Enjoy chatting! 🎉
