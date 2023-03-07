import os

from django.db import models as m

from django.contrib.auth.models import User

from uuid import uuid4 as u4

def upload_photo(instance, filename):

    file_extenstion = filename.split('.')[-1]
    new_filename = f"{u4}.{file_extenstion}"

    return os.path.join('uploads/note/images', new_filename)

class Photo(m.Model):

    uid = m.UUIDField(default = u4)

    uploader = m.ForeignKey(User, on_delete = m.CASCADE)

    note = m.ForeignKey('Note', on_delete = m.CASCADE)

    file = m.ImageField(upload_to = upload_photo)

    uploaded_at = m.DateTimeField(auto_now_add = True)

    def __str__(self):

        return self.uploader.profile.name

class Note(m.Model):

    uid = m.UUIDField(default = u4) # unique id

    author = m.ForeignKey(User, on_delete = m.CASCADE)
    #co_authors = m.ManyToManyField(User, blank = True, related_name = 'note_coauthors') # author != co-author

    folders = m.ManyToManyField('Folder', blank = True, related_name = 'note_folders')

    title = m.TextField()
    content = m.TextField()

    photos = m.ManyToManyField(Photo, blank = True, related_name = 'note_photos')

    loved = m.BooleanField(default = False)
    pinned = m.BooleanField(default = False)
    archived = m.BooleanField(default = False)

    deleted = m.BooleanField(default = False)
    deleted_at = m.DateTimeField(auto_now = True)

    created_at = m.DateTimeField(auto_now_add = True)
    updated_at = m.DateTimeField(auto_now = True)

    def __str__(self):

        return self.author.username

    class Meta:

        ordering = ['-updated_at']

class Folder(m.Model):

    uid = m.UUIDField(default = u4)

    author = m.ForeignKey(User, on_delete = m.CASCADE)

    title = m.CharField(max_length = 50)

    created_at = m.DateTimeField(auto_now_add = True)
    updated_at = m.DateTimeField(auto_now = True)

    def __str__(self):

        return self.title

    class Meta:

        ordering = ['-updated_at']