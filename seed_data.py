import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'study_collab.settings')
django.setup()

from django.contrib.auth.models import User
from main.models import Profile, Subject, UserLevel

def seed():
    # Create subjects
    maths, _ = Subject.objects.get_or_create(name="Mathematics")
    physics, _ = Subject.objects.get_or_create(name="Physics")
    cs, _ = Subject.objects.get_or_create(name="Computer Science")

    # Create users
    # Student Beginner
    if not User.objects.filter(username='student1').exists():
        u1 = User.objects.create_user('student1', 'student1@example.com', 'pass123')
        Profile.objects.create(user=u1, role='student')
        UserLevel.objects.create(user=u1, subject=maths, level='beginner')
        print("Created student1 (Beginner in Maths)")

    # Expert/Teacher
    if not User.objects.filter(username='expert1').exists():
        u2 = User.objects.create_user('expert1', 'expert1@example.com', 'pass123')
        Profile.objects.create(user=u2, role='teacher')
        UserLevel.objects.create(user=u2, subject=maths, level='pro')
        print("Created expert1 (Pro in Maths)")

    # Intermediate Student
    if not User.objects.filter(username='student2').exists():
        u3 = User.objects.create_user('student2', 'student2@example.com', 'pass123')
        Profile.objects.create(user=u3, role='student')
        UserLevel.objects.create(user=u3, subject=maths, level='intermediate')
        print("Created student2 (Intermediate in Maths)")

if __name__ == "__main__":
    seed()
