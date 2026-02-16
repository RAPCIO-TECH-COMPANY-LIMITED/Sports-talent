from django.urls import path
from . views import home,register,upload_video,discover_talents,player_dashboard,login_redirect,player_detail,pricing_page
from django.contrib.auth import views as auth_views
from .views import manage_roster,edit_roster_player,add_roster_player,delete_roster_player,ai_tools
urlpatterns = [
    path('', home, name='home'),
    
    path('register/',register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    # Player-specific URLs
    path('dashboard/', player_dashboard, name='player_dashboard'),
    path('upload/', upload_video, name='upload_video'),

    # Club-specific URLs
    path('discover/', discover_talents, name='discover_talents'),
    path('redirect/', login_redirect, name='login_redirect'),
    
    path('player/<int:pk>/', player_detail, name='player_detail'),
    path('pricing/', pricing_page, name='pricing'),

    path('roster/', manage_roster, name='manage_roster'),
    path('roster/add/', add_roster_player, name='add_roster_player'),
    path('roster/edit/<int:pk>/', edit_roster_player, name='edit_roster_player'),
    path('roster/delete/<int:pk>/', delete_roster_player, name='delete_roster_player'),

    path('ai-tools/', ai_tools, name='ai_tools'),
    ]