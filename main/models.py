from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    study_hours_goal = models.IntegerField(default=15)
    problems_solved_goal = models.IntegerField(default=20)
    chapters_read_goal = models.IntegerField(default=2)
    sessions_attended_goal = models.IntegerField(default=3)
    
    study_hours_done = models.IntegerField(default=12)
    problems_solved_done = models.IntegerField(default=14)
    chapters_read_done = models.IntegerField(default=1)
    sessions_attended_done = models.IntegerField(default=2)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

class Subject(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, default="code") # FontAwesome or Lucide icon name
    
    def __str__(self):
        return self.name

class UserLevel(models.Model):
    LEVEL_CHOICES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('pro', 'Pro'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)

    class Meta:
        unique_together = ('user', 'subject')

class Task(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True)
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

class Connection(models.Model):
    user1 = models.ForeignKey(User, related_name='connections1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='connections2', on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user1.username} & {self.user2.username} ({self.subject.name})"

class ChatMessage(models.Model):
    connection = models.ForeignKey(Connection, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class SharedNote(models.Model):
    connection = models.OneToOneField(Connection, on_delete=models.CASCADE, related_name='note')
    content = models.TextField(default="")
    last_updated = models.DateTimeField(auto_now=True)
