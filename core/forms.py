from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, PlayerProfile, ClubProfile,Video, Subscription,AcademyProfile
from django.db import transaction


class PlayerSignUpForm(UserCreationForm):
    country = forms.CharField(max_length=100)
    position = forms.CharField(max_length=50)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta(UserCreationForm.Meta):
        model = CustomUser

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.user_type = 'player'
        user.save()
        PlayerProfile.objects.create(
            user=user,
            country=self.cleaned_data.get('country'),
            position=self.cleaned_data.get('position'),
            date_of_birth=self.cleaned_data.get('date_of_birth')
        )
        return user

class ClubSignUpForm(UserCreationForm):
    club_name = forms.CharField(max_length=200)
    country = forms.CharField(max_length=100)

    class Meta(UserCreationForm.Meta):
        model = CustomUser

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.user_type = 'club'
        user.save()
        ClubProfile.objects.create(
            user=user,
            club_name=self.cleaned_data.get('club_name'),
            country=self.cleaned_data.get('country')
        )
        return user

class AcademySignUpForm(UserCreationForm):
    academy_name = forms.CharField(max_length=200)
    location = forms.CharField(max_length=100)

    class Meta(UserCreationForm.Meta):
        model = CustomUser

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.user_type = 'academy'
        user.save()
        AcademyProfile.objects.create(
            user=user,
            academy_name=self.cleaned_data.get('academy_name'),
            location=self.cleaned_data.get('location')
        )
        return user

class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'video_file']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g., Best Goals of the Season'}),
        }

