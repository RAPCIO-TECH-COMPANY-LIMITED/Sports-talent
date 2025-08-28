from django.contrib import admin
from . models import CustomUser, PlayerProfile, ClubProfile,Video
# Register your models here.
admin.site.site_header = "EA Football Talent Admin"
admin.site.site_title = "EA Football Talent Admin Portal"
admin.site.index_title = "Welcome to EA Football Talent Admin"
admin.site.register([CustomUser, PlayerProfile, ClubProfile, Video])