from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, PlayerProfile, ClubProfile, Video, Subscription, AcademyProfile
from django.db import transaction
import uuid

class UserRegistrationForm(UserCreationForm):
    user_type = forms.ChoiceField(choices=CustomUser.USER_TYPE_CHOICES, required=True)
    country = forms.CharField(max_length=100, required=False)
    first_name = forms.CharField(max_length=100, required=False)
    last_name = forms.CharField(max_length=100, required=False)
    date_of_birth = forms.DateField(widget=forms.SelectDateWidget(), required=False)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('email', 'user_type')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = self.cleaned_data.get('user_type')
        if commit:
            user.save()
            user_type = self.cleaned_data.get('user_type')
            if user_type == 'player':
                PlayerProfile.objects.create(
                    user=user,
                    country=self.cleaned_data.get('country'),
                    date_of_birth=self.cleaned_data.get('date_of_birth') or '2000-01-01'
                )
            elif user_type == 'club':
                ClubProfile.objects.create(user=user, club_name=user.username)
            elif user_type == 'academy':
                AcademyProfile.objects.create(user=user, academy_name=user.username)
        return user

class PlayerSignUpForm(UserCreationForm):
    country = forms.CharField(max_length=100)
    position = forms.CharField(max_length=50)
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
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
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            position=self.cleaned_data.get('position'),
            date_of_birth=self.cleaned_data.get('date_of_birth')
        )
        return user

class ClubSignUpForm(UserCreationForm):
    club_name = forms.CharField(max_length=200)
    region = forms.CharField(max_length=100)
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
            region=self.cleaned_data.get('region'),
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

class PlayerManagementForm(forms.ModelForm):
    country = forms.CharField(max_length=100)
    position = forms.CharField(max_length=50)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email']

    @transaction.atomic
    def save(self, club=None, academy=None):
        user = super().save(commit=False)

        if not user.pk:
            user.username = user.email if user.email else f"player_{uuid.uuid4().hex[:8]}"
            user.set_unusable_password()
            user.user_type = 'player'

        user.save()

        defaults = {
            'country': self.cleaned_data.get('country'),
            'position': self.cleaned_data.get('position'),
            'date_of_birth': self.cleaned_data.get('date_of_birth'),
        }

        # Assign affiliation based on what was passed
        if club:
            defaults['club'] = club
        if academy:
            defaults['academy'] = academy

        PlayerProfile.objects.update_or_create(
            user=user,
            defaults=defaults
        )
        return user