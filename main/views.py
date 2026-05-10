from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Subject, UserLevel, Connection, ChatMessage, SharedNote, Profile, Task
from .forms import SignUpForm, ProfileUpdateForm
from django.db.models import Q

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data.get('role')
            Profile.objects.create(user=user, role=role)
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def profile_settings(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ProfileUpdateForm(instance=profile)
    return render(request, 'profile_settings.html', {'form': form})

@login_required
def dashboard(request):
    subjects = Subject.objects.all()
    # If no subjects, create some defaults with icons matching the image
    if not subjects.exists():
        default_subjects = [
            ("Data Structures", "code"),
            ("Operating Systems", "settings"),
            ("Database Systems", "database"),
            ("Computer Networks", "share-2"),
            ("Software Engineering", "file-text"),
            ("Web Development", "globe"),
            ("Python Programming", "terminal"),
        ]
        for name, icon in default_subjects:
            Subject.objects.create(name=name, icon=icon)
        subjects = Subject.objects.all()
    
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    # Create some tasks if none exist to match the image
    tasks = Task.objects.filter(user=request.user)
    if not tasks.exists():
        ds_subject = Subject.objects.filter(name="Data Structures").first()
        os_subject = Subject.objects.filter(name="Operating Systems").first()
        db_subject = Subject.objects.filter(name="Database Systems").first()
        web_subject = Subject.objects.filter(name="Web Development").first()
        
        from datetime import time
        Task.objects.create(user=request.user, title="Study Arrays in Data Structures", subject=ds_subject, time=time(14, 0), status='in_progress')
        Task.objects.create(user=request.user, title="Solve 5 Problems on Arrays", subject=ds_subject, time=time(11, 30), status='completed')
        Task.objects.create(user=request.user, title="Read Chapter 5 - OS", subject=os_subject, time=time(16, 0), status='pending')
        Task.objects.create(user=request.user, title="Database Normalization Notes", subject=db_subject, time=time(18, 30), status='pending')
        Task.objects.create(user=request.user, title="Attend Study Session", subject=web_subject, time=time(20, 0), status='pending')
        tasks = Task.objects.filter(user=request.user)

    # Create some mock partners/users if they don't exist
    partners_data = [
        ("rahul", "Rahul Verma", "intermediate", "DS, OS"),
        ("sneha", "Sneha Iyer", "pro", "DBMS, CN"),
        ("arjun", "Arjun Mehta", "pro", "DS, Algorithms"),
        ("kavya", "Kavya Nair", "intermediate", "OS, SE"),
        ("aditya", "Aditya Singh", "pro", "DBMS, DS"),
    ]
    
    other_users = []
    for username, full_name, level, subs in partners_data:
        u, created = User.objects.get_or_create(username=username, defaults={'first_name': full_name.split()[0], 'last_name': full_name.split()[1]})
        p, _ = Profile.objects.get_or_create(user=u, defaults={'role': 'student'})
        other_users.append({'user': u, 'level': level, 'subjects': subs})

    # For "Find Study Partners", let's just pass all other students
    partners = other_users

    # Online users (sidebar)
    online_users = other_users[:4]

    role = profile.role
    if role == 'student':
        context = {
            'subjects': subjects,
            'tasks': tasks,
            'partners': partners,
            'online_users': online_users,
            'profile': profile,
        }
        return render(request, 'dashboard.html', context)
    else:
        return render(request, 'staff_dashboard.html', {'subjects': subjects})

@login_required
def staff_dashboard(request):
    total_students = Profile.objects.filter(role='student').count()
    subjects = Subject.objects.all()
    active_chats = Connection.objects.count()
    notifications = 0  # placeholder
    recent_requests = UserLevel.objects.select_related('user', 'subject').order_by('-id')[:5]
    context = {
        'total_students': total_students,
        'subjects': subjects,
        'active_chats': active_chats,
        'notifications': notifications,
        'recent_requests': recent_requests,
    }
    return render(request, 'staff_dashboard.html', context)

@login_required
def subject_detail(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    user_level = UserLevel.objects.filter(user=request.user, subject=subject).first()
    
    # Subject-specific tasks
    tasks = Task.objects.filter(user=request.user, subject=subject)
    
    # Recommended partners for this subject
    # (In a real app, this would be more complex logic)
    partners = Profile.objects.filter(role='student').exclude(user=request.user)[:3]
    
    context = {
        'active_subject': subject,
        'user_level': user_level,
        'tasks': tasks,
        'partners': partners,
    }
    return render(request, 'subject_detail.html', context)

@login_required
def select_level(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    if request.method == 'POST':
        level = request.POST.get('level')
        user_level, created = UserLevel.objects.update_or_create(
            user=request.user, subject=subject,
            defaults={'level': level}
        )
        return redirect('subject_detail', subject_id=subject.id)
    
    return render(request, 'select_level.html', {'active_subject': subject})

@login_required
def connect_public(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    my_level_obj = get_object_or_404(UserLevel, user=request.user, subject=subject)
    
    if my_level_obj.level != 'beginner':
        return redirect('dashboard') # Only beginners trigger "connect public" from their side usually
    
    # Try to find a partner (Intermediate or Pro)
    potential_partners = UserLevel.objects.filter(
        subject=subject,
        level__in=['intermediate', 'pro']
    ).exclude(user=request.user)
    
    if potential_partners.exists():
        partner = potential_partners.first().user
        # Check if connection already exists
        connection = Connection.objects.filter(
            (Q(user1=request.user) & Q(user2=partner) & Q(subject=subject)) |
            (Q(user1=partner) & Q(user2=request.user) & Q(subject=subject))
        ).first()
        
        if not connection:
            connection = Connection.objects.create(user1=request.user, user2=partner, subject=subject)
            SharedNote.objects.get_or_create(connection=connection)
            
        return redirect('study_room', connection_id=connection.id)
    
    return render(request, 'no_partner.html', {'subject': subject})

@login_required
def study_room(request, connection_id):
    connection = get_object_or_404(Connection, id=connection_id)
    if request.user != connection.user1 and request.user != connection.user2:
        return redirect('dashboard')
    
    if request.method == 'POST':
        # Handle chat message or note update
        if 'message' in request.POST:
            content = request.POST.get('message')
            ChatMessage.objects.create(connection=connection, sender=request.user, content=content)
        elif 'note' in request.POST:
            content = request.POST.get('note')
            note = connection.note
            note.content = content
            note.save()
            
    messages = connection.messages.all().order_by('timestamp')
    note = connection.note
    opponent = connection.user2 if request.user == connection.user1 else connection.user1
    
    return render(request, 'study_room.html', {
        'connection': connection,
        'messages': messages,
        'note': note,
        'opponent': opponent
    })

@login_required
def create_connection(request, subject_id, partner_id):
    subject = get_object_or_404(Subject, id=subject_id)
    partner = get_object_or_404(User, id=partner_id)
    
    # Check if connection already exists
    connection = Connection.objects.filter(
        (Q(user1=request.user) & Q(user2=partner) & Q(subject=subject)) |
        (Q(user1=partner) & Q(user2=request.user) & Q(subject=subject))
    ).first()
    
    if not connection:
        connection = Connection.objects.create(user1=request.user, user2=partner, subject=subject)
        SharedNote.objects.get_or_create(connection=connection)
        
    return redirect('study_room', connection_id=connection.id)

def logout_view(request):
    logout(request)
    return redirect('login')
