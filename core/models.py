from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('player', 'Player'),
        ('club', 'Club'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)

class PlayerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    country = models.CharField(max_length=100)
    position = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username

class ClubProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    club_name = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.club_name

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