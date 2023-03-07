from django.db import models as m

from django.contrib.auth.models import User

from django.dispatch import receiver
from django.db.models.signals import post_save

class Profile(m.Model):

    user = m.OneToOneField(User, on_delete = m.CASCADE, related_name = 'profile')

    name = m.CharField(max_length = 100)

    initials = m.CharField(max_length = 3)

    premium = m.BooleanField(default = False)
    premium_since = m.DateTimeField(blank = True, null = True)
    
    premium_invite_uid = m.CharField(max_length = 7)
    premium_friend_offer_shown = m.BooleanField(default = False)

    invited_by = m.ForeignKey('Profile', on_delete = m.DO_NOTHING, blank = True, null = True)
    invited_friends = m.ManyToManyField('Profile', blank = True, related_name = 'friends_invited')

    dark_mode = m.BooleanField(default = False)

    password_recovery_token = m.TextField(blank = True, null = True)

    def __str__(self):
        
        return self.name

    class Meta:

        ordering = ['-name']

@receiver(post_save, sender = User)
def create_user_profile(sender, instance, created, **kwargs):

    if created:

        Profile.objects.create(user = instance)
    