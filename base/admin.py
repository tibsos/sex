from django.contrib import admin as a
from .models import *

a.site.register(Info)

class MessageAdmin(a.ModelAdmin):
    list_display = ('user', 'name', 'email', 'topic', 'created_at', 'resolved')

a.site.register(Message, MessageAdmin)