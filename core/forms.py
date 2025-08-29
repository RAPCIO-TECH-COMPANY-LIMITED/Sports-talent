from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, PlayerProfile, ClubProfile,Video, Subscription

class PlayerSignUpForm(UserCreationForm):
    country = forms.CharField(max_length=100)
    position = forms.CharField(max_length=50)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'player'
        if commit:
            user.save()
            PlayerProfile.objects.create(
                user=user,
                country=self.cleaned_data.get('country'),
                position=self.cleaned_data.get('position'),
                date_of_birth=self.cleaned_data.get('date_of_birth'),
            )
        return user

class ClubSignUpForm(UserCreationForm):
    club_name = forms.CharField(max_length=200)
    country = forms.CharField(max_length=100)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'club'
        if commit:
            user.save()
            club_profile = ClubProfile.objects.create(
                user=user,
                club_name=self.cleaned_data.get('club_name'),
                country=self.cleaned_data.get('country'),
            )
            Subscription.objects.create(club=club_profile, tier='free', is_active=True)
        return user
    

class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'video_file']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g., Best Goals of the Season'}),
        }