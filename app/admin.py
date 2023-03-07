from django.contrib import admin as a

from .models import *

@a.register(Photo)
class PhotoAdmin(a.ModelAdmin):

    list_display = ['profile_name', 'image_size']

    def profile_name(self, image):

        return image.uploader.profile.name

    def image_size(self, image):

        size_in_MB = round(image.file.size / 1024 / 1024, 2)

        return f"{size_in_MB} MB"

a.site.register(Note)
a.site.register(Folder)

