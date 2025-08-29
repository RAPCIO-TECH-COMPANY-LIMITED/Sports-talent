from django.shortcuts import render, redirect, get_object_or_404
from .forms import PlayerSignUpForm, ClubSignUpForm,VideoUploadForm
from django.contrib.auth.decorators import login_required
from .models import PlayerProfile
from .tasks import analyze_video_for_tags

# Create your views here.
def home(request):
    return render(request, 'index.html')


def register(request):
    player_form = PlayerSignUpForm()
    club_form = ClubSignUpForm()

    if request.method == 'POST':
        if 'register_player' in request.POST:
            # If a player is registering, populate the player_form with POST data
            player_form = PlayerSignUpForm(request.POST)
            if player_form.is_valid():
                player_form.save()
                return redirect('login')
        
        elif 'register_club' in request.POST:
            # If a club is registering, populate the club_form with POST data
            club_form = ClubSignUpForm(request.POST)
            if club_form.is_valid():
                club_form.save()
                return redirect('login')

    # The context will now always have valid forms to render
    context = {
        'player_form': player_form,
        'club_form': club_form
    }
    return render(request, 'register.html', context)

@login_required
def upload_video(request):
    if request.user.user_type != 'player':
        return redirect('home')

    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            # Assign the logged-in player's profile to the video
            video.player = request.user.playerprofile
            video.save()
            # Trigger the Celery task to analyze the video
            analyze_video_for_tags.delay(video.id)
            return redirect('player_dashboard')
    else:
        form = VideoUploadForm()
    
    return render(request, 'upload_video.html', {'form': form})

@login_required
def discover_talents(request):
    if request.user.user_type != 'club':
        return redirect('home')

    # Get all player profiles
    players = PlayerProfile.objects.all()
    context = {
        'players': players
    }
    return render(request, 'discover_talents.html', context)

@login_required
def player_dashboard(request):
    # Ensure the user is a player
    if request.user.user_type != 'player':
        return redirect('home') # Or an error page

    profile = PlayerProfile.objects.get(user=request.user)
    videos = profile.videos.all() # Get all videos related to this player's profile

    context = {
        'profile': profile,
        'videos': videos
    }
    return render(request, 'player_dashboard.html', context)

@login_required
def login_redirect(request):
    """
    Redirects users to their respective dashboards based on their user_type.
    """
    if request.user.user_type == 'player':
        return redirect('player_dashboard')
    elif request.user.user_type == 'club':
        return redirect('discover_talents')
    else:
        # Fallback for any other user type or unexpected case
        return redirect('home')
    
@login_required
def player_detail(request, pk):
    # This view is for clubs to see player details.
    # You might want to restrict access to only clubs.
    if request.user.user_type != 'club':
        return redirect('home')

    # Fetch the specific player profile using its primary key (pk), or return a 404 error if not found.
    player_profile = get_object_or_404(PlayerProfile, pk=pk)
    
    context = {
        'player': player_profile
    }
    return render(request, 'player_detail.html', context)