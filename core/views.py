from django.shortcuts import render, redirect, get_object_or_404
from .forms import PlayerSignUpForm, ClubSignUpForm,VideoUploadForm,AcademySignUpForm
from django.contrib.auth.decorators import login_required
from .models import PlayerProfile
from .tasks import analyze_video_for_tags
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
from datetime import timedelta
from .models import ClubProfile, Subscription
from django.utils import timezone



# Create your views here.
def home(request):
    return render(request, 'index.html')


def register(request):
    player_form = PlayerSignUpForm()
    club_form = ClubSignUpForm()
    academy_form = AcademySignUpForm()

    if request.method == 'POST':
        if 'register_player' in request.POST:
            player_form = PlayerSignUpForm(request.POST)
            if player_form.is_valid():
                player_form.save()
                return redirect('login')

        elif 'register_club' in request.POST:
            club_form = ClubSignUpForm(request.POST)
            if club_form.is_valid():
                club_form.save()
                return redirect('login')

        elif 'register_academy' in request.POST:
            academy_form = AcademySignUpForm(request.POST)
            if academy_form.is_valid():
                academy_form.save()
                return redirect('login')

    return render(request, 'register.html', {
        'player_form': player_form,
        'club_form': club_form,
        'academy_form': academy_form
    })

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
    if request.user.user_type != 'club':
        return redirect('home')

    # This is the robust way to check for an active subscription
    try:
        is_subscribed = request.user.clubprofile.subscription.is_active
    except Subscription.DoesNotExist:
        is_subscribed = False # If no subscription object exists, they are not subscribed
    
    # We will expand this logic to check for 'pro' tier later
    if not is_subscribed:
        return redirect('pricing_page')

    player_profile = get_object_or_404(PlayerProfile, pk=pk)
    
    context = {
        'player': player_profile
    }
    return render(request, 'player_detail.html', context)

def pricing_page(request):
    return render(request, 'pricing.html')


@csrf_exempt # Required for webhooks from external services
def flutterwave_webhook(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        # 1. Verify the webhook is authentic from Flutterwave (they have a process for this)
        
        # 2. Check if the payment was successful
        if payload['status'] == 'successful':
            # 3. Find the user in your database based on info in the payload
            club_user_email = payload['customer']['email']
            club_profile = ClubProfile.objects.get(user__email=club_user_email)
            
            # 4. Update their subscription
            subscription, created = Subscription.objects.get_or_create(club=club_profile)
            subscription.tier = 'pro'
            subscription.is_active = True
            subscription.end_date = timezone.now() + timedelta(days=30) # Grant 30 days of access
            subscription.save()
            
        return HttpResponse(status=200) # Let Flutterwave know you received it