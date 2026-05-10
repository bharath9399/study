from django.urls import path
from . import views, api_views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('staff_dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('subject/<int:subject_id>/', views.subject_detail, name='subject_detail'),
    path('subject/<int:subject_id>/level/', views.select_level, name='select_level'),
    path('subject/<int:subject_id>/connect/', views.connect_public, name='connect_public'),
    path('subject/<int:subject_id>/connect/<int:partner_id>/', views.create_connection, name='create_connection'),
    path('study/<int:connection_id>/', views.study_room, name='study_room'),
    path('profile/', views.profile_settings, name='profile_settings'),
    
    # API endpoints
    path('api/register/', api_views.RegisterAPIView.as_view(), name='api_register'),
    path('api/login/', api_views.LoginAPIView.as_view(), name='api_login'),
    path('api/logout/', api_views.LogoutAPIView.as_view(), name='api_logout'),
    path('api/profile/', api_views.ProfileAPIView.as_view(), name='api_profile'),
    path('api/tasks/', api_views.TasksAPIView.as_view(), name='api_tasks'),
    path('api/online-students/', api_views.OnlineStudentsAPIView.as_view(), name='api_online_students'),
    path('api/connections/', api_views.ConnectedPartnersAPIView.as_view(), name='api_connections'),
]
