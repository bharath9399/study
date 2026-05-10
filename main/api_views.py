from rest_framework import status, views, permissions
from rest_framework.response import Response
from django.contrib.auth import login, logout, authenticate
from .serializers import UserSerializer, ProfileSerializer, TaskSerializer, SubjectSerializer
from .models import Profile, Task, UserLevel, Connection, Subject
from django.contrib.auth.models import User
from django.db.models import Q

class RegisterAPIView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            role = request.data.get('role', 'student')
            Profile.objects.create(user=user, role=role)
            return Response({
                "message": "User registered successfully",
                "user": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginAPIView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({
                "message": "Login successful",
                "username": user.username,
                "role": user.profile.role
            }, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutAPIView(views.APIView):
    def post(self, request):
        logout(request)
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)

class ProfileAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

class TasksAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        tasks = Task.objects.filter(user=request.user)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

class OnlineStudentsAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        other_students = Profile.objects.filter(role='student').exclude(user=request.user)[:5]
        data = []
        for profile in other_students:
            level_obj = UserLevel.objects.filter(user=profile.user).first()
            data.append({
                "username": profile.user.username,
                "full_name": f"{profile.user.first_name} {profile.user.last_name}",
                "level": level_obj.level if level_obj else "Beginner"
            })
        return Response(data)

class ConnectedPartnersAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        connections = Connection.objects.filter(Q(user1=request.user) | Q(user2=request.user))
        data = []
        for conn in connections:
            partner = conn.user2 if conn.user1 == request.user else conn.user1
            data.append({
                "connection_id": conn.id,
                "partner_name": f"{partner.first_name} {partner.last_name}",
                "subject": conn.subject.name,
                "created_at": conn.created_at
            })
        return Response(data)
