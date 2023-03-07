from django.shortcuts import render

from user.models import Profile
from analytics.models import Funnel
from app.models import Folder, Note


def overview(request):

    if request.user.username == '_':

        c = {}

        c['landing_visits'] = Funnel.objects.all().filter(stage = '0').count()
        c['register_visits'] = Funnel.objects.all().filter(stage = '1').count()
        c['users'] = Profile.objects.all().count()
        c['premium_users'] = Profile.objects.all().filter(premium = True).count()

        c['notepads'] = Folder.objects.all().count()
        c['notes'] = Note.objects.all().count()

        return render(request, 'overview.html', c)