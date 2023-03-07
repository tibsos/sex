from django.db import models as m

from django.contrib.auth.models import User

from tinymce.models import HTMLField

class Info(m.Model):

    title = m.TextField()
    content = HTMLField()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
        
class Message(m.Model):
    
    user = m.ForeignKey(User, on_delete = m.CASCADE, blank = True, null = True)
    
    name = m.TextField(blank = True)
    email = m.TextField(blank = True)
    
    topic = m.TextField()
    message = m.TextField()
    
    resolved = m.BooleanField(default = False)

    created_at = m.DateTimeField(auto_now_add = True)
    resolved_at = m.DateTimeField(auto_now = True)
    
    class Meta:
        ordering = ['-created_at']