from django.urls import path
from . views import home,register,upload_video,discover_talents,player_dashboard,login_redirect,player_detail,pricing_page
from django.contrib.auth import views as auth_views
from .views import manage_club_players,add_club_player,edit_club_player,delete_club_player
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

    path('club/roster/',manage_club_players, name='manage_club_players'),
    path('club/player/add/',add_club_player, name='add_club_player'),
    path('club/player/edit/<int:pk>/',edit_club_player, name='edit_club_player'),
    path('club/player/delete/<int:pk>/',delete_club_player, name='delete_club_player'),
    ]