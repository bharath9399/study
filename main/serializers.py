from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Subject, Task

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'icon']

class TaskSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    
    class Meta:
        model = Task
        fields = ['id', 'title', 'subject', 'subject_name', 'time', 'status']

class ProfileSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)

    class Meta:
        model = Profile
        fields = [
            'user_details', 'role', 'avatar', 
            'study_hours_goal', 'problems_solved_goal', 'chapters_read_goal', 'sessions_attended_goal',
            'study_hours_done', 'problems_solved_done', 'chapters_read_done', 'sessions_attended_done'
        ]
