from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('player', 'Player'),
        ('club', 'Club'),
        ('academy', 'Academy'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)

class AcademyProfile(models.Model):
    """Stores information specific to Academies."""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    academy_name = models.CharField(max_length=200)
    location = models.CharField(max_length=100)
    website = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.academy_name

class ClubProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    club_name = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.club_name

class PlayerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    country = models.CharField(max_length=100)
    position = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    bio = models.TextField(blank=True, null=True)
    club = models.ForeignKey(ClubProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='players')
    academy = models.ForeignKey(AcademyProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='players')

    def __str__(self):
        return self.user.username


class Video(models.Model):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=200)
    video_file = models.FileField(upload_to='videos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.player.user.username}"

class VideoTag(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='tags')
    tag = models.CharField(max_length=100)
    start_time = models.FloatField()
    end_time = models.FloatField()

    def __str__(self):
        return f"{self.tag} for {self.video.title}"
    
class Subscription(models.Model):
    TIER_CHOICES = (
        ('free', 'Free'),
        ('pro', 'Pro'),
    )
    club = models.OneToOneField(ClubProfile, on_delete=models.CASCADE)
    tier = models.CharField(max_length=10, choices=TIER_CHOICES, default='free')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.club.club_name} - {self.tier.capitalize()} Tier"