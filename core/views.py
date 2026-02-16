from django.shortcuts import render, redirect, get_object_or_404
from .forms import PlayerSignUpForm, ClubSignUpForm, VideoUploadForm, AcademySignUpForm, PlayerManagementForm
from django.contrib.auth.decorators import login_required
from .models import PlayerProfile, ClubProfile, Subscription, AcademyProfile
from .tasks import analyze_video_for_tags
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
from datetime import timedelta
from django.utils import timezone


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
            video.player = request.user.playerprofile
            video.save()
            analyze_video_for_tags.delay(video.id)
            return redirect('player_dashboard')
    else:
        form = VideoUploadForm()
    return render(request, 'upload_video.html', {'form': form})

# GLOBAL VIEW: Visible to all (but actions may restrict)
def discover_talents(request):
    # Fetch ALL players for the public directory
    players = PlayerProfile.objects.all().select_related('user', 'club', 'academy')

    # Filter lists
    positions = PlayerProfile.objects.values_list('position', flat=True).distinct().order_by('position')
    clubs = ClubProfile.objects.values_list('club_name', flat=True).distinct()
    academies = AcademyProfile.objects.values_list('academy_name', flat=True).distinct()
    affiliations = sorted(list(clubs) + list(academies))

    context = {
        'players': players,
        'positions': positions,
        'affiliations': affiliations,
    }
    return render(request, 'discover_talents.html', context)

@login_required
def player_dashboard(request):
    if request.user.user_type != 'player':
        return redirect('home')
    profile = PlayerProfile.objects.get(user=request.user)
    videos = profile.videos.all()
    context = {'profile': profile, 'videos': videos}
    return render(request, 'player_dashboard.html', context)

@login_required
def login_redirect(request):
    if request.user.user_type == 'player':
        return redirect('player_dashboard')
    elif request.user.user_type in ['club', 'academy']:
        return redirect('manage_roster')
    else:
        return redirect('home')

@login_required
def player_detail(request, pk):
    # Security check: Only clubs/academies can view details
    if request.user.user_type not in ['club', 'academy']:
        return redirect('home')

    # Subscription Logic
    is_subscribed = False
    if request.user.user_type == 'club':
        try:
            is_subscribed = request.user.clubprofile.subscription.is_active
        except (ClubProfile.DoesNotExist, Subscription.DoesNotExist):
            is_subscribed = False
    elif request.user.user_type == 'academy':
        # Academies might have free access or different logic
        is_subscribed = True

    if not is_subscribed:
        return redirect('pricing_page')

    player_profile = get_object_or_404(PlayerProfile, pk=pk)
    context = {'player': player_profile}
    return render(request, 'player_detail.html', context)

def pricing_page(request):
    return render(request, 'pricing.html')

@csrf_exempt
def flutterwave_webhook(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        if payload['status'] == 'successful':
            club_user_email = payload['customer']['email']
            club_profile = ClubProfile.objects.get(user__email=club_user_email)
            subscription, created = Subscription.objects.get_or_create(club=club_profile)
            subscription.tier = 'pro'
            subscription.is_active = True
            subscription.end_date = timezone.now() + timedelta(days=30)
            subscription.save()
    return HttpResponse(status=200)


@login_required
def manage_roster(request):
    """
    Displays ONLY players belonging to the logged-in club or academy.
    This supports the separate template for management.
    """
    if request.user.user_type not in ['club', 'academy']:
        return redirect('home')

    players = []
    org_name = ""

    # Determine organization type and filter players strictly by that relation
    if request.user.user_type == 'club':
        profile = get_object_or_404(ClubProfile, user=request.user)
        players = PlayerProfile.objects.filter(club=profile).select_related('user')
        org_name = profile.club_name
    elif request.user.user_type == 'academy':
        profile = get_object_or_404(AcademyProfile, user=request.user)
        players = PlayerProfile.objects.filter(academy=profile).select_related('user')
        org_name = profile.academy_name

    # Helper for the dropdown filter in the management view
    positions = players.values_list('position', flat=True).distinct().order_by('position')

    return render(request, 'manage_players.html', {
        'players': players,
        'org_name': org_name,
        'positions': positions
    })

@login_required
def add_roster_player(request):
    """Allows a club/academy to register a new player specifically to their roster."""
    if request.user.user_type not in ['club', 'academy']:
        return redirect('home')

    if request.method == 'POST':
        form = PlayerManagementForm(request.POST)
        if form.is_valid():
            # Pass the correct affiliation based on user type
            if request.user.user_type == 'club':
                form.save(club=request.user.clubprofile)
            else:
                form.save(academy=request.user.academyprofile)
            return redirect('manage_roster')
    else:
        form = PlayerManagementForm()

    return render(request, 'player_form.html', {'form': form, 'title': 'Add New Player'})

@login_required
def edit_roster_player(request, pk):
    """Update existing player details. Securely checks ownership."""
    # 1. Fetch player ensuring they belong to the requestor
    if request.user.user_type == 'club':
        profile = request.user.clubprofile
        player_profile = get_object_or_404(PlayerProfile, pk=pk, club=profile)
    elif request.user.user_type == 'academy':
        profile = request.user.academyprofile
        player_profile = get_object_or_404(PlayerProfile, pk=pk, academy=profile)
    else:
        return redirect('home')

    player_user = player_profile.user

    if request.method == 'POST':
        form = PlayerManagementForm(request.POST, instance=player_user)
        if form.is_valid():
            if request.user.user_type == 'club':
                form.save(club=profile)
            else:
                form.save(academy=profile)
            return redirect('manage_roster')
    else:
        initial_data = {
            'country': player_profile.country,
            'position': player_profile.position,
            'date_of_birth': player_profile.date_of_birth,
        }
        form = PlayerManagementForm(instance=player_user, initial=initial_data)

    return render(request, 'player_form.html', {'form': form, 'title': 'Update Player'})

@login_required
def delete_roster_player(request, pk):
    """Remove a player from the roster."""
    if request.user.user_type == 'club':
        player = get_object_or_404(PlayerProfile, pk=pk, club=request.user.clubprofile)
    elif request.user.user_type == 'academy':
        player = get_object_or_404(PlayerProfile, pk=pk, academy=request.user.academyprofile)
    else:
        return redirect('home')

    if request.method == 'POST':
        player.user.delete()
        return redirect('manage_roster')
    return render(request, 'confirm_delete.html', {'player': player})

# @login_required
def ai_tools(request):
    """Renders the AI Performance Center powered by Gemini."""
    return render(request, 'ai_tools.html')