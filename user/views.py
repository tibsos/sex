from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse 

from django.contrib.auth.decorators import login_required as lr

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

from user.models import Profile
from analytics.models import Funnel

import string
import random

from datetime import datetime as dt

def log_in(request):

    c = {}

    if request.method == 'POST':

        u = authenticate(

            username = request.POST.get('u'),
            password = request.POST.get('p'),

        )

        if u:

            login(request, u)
            return redirect('/home/')

        else: 

            return render(request, 'auth/login.html', {'e': True})

    return render(request, 'auth/login.html')

def register(request):

    if not Funnel.objects.filter(stage = '1').filter(ip = request.headers['host']).exists():

        Funnel.objects.create(

            stage = '1',
            ip = request.headers['host'],

        )

    if request.method == 'POST':

        name = request.POST.get('n')

        username = request.POST.get('u')
        password = request.POST.get('p')

        user = User(username = username)
        user.set_password(password)
        user.save()

        user.profile.name = name
        user.profile.initials = ''.join(letter[0].upper() for letter in name.split(' '))[0:3]

        uid = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(7))

        while True:
            if Profile.objects.filter(premium_invite_uid = uid).exists():
                uid = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(7))
            else:
                break

        user.profile.premium_invite_uid = uid
        user.profile.save()

        user = authenticate(username = username, password = password)
        login(request, user)

        return redirect('/home/')

    return render(request, 'auth/register.html')

def invited_register(request, premium_invite_uid):

    invited_profile = Profile.objects.filter(premium_invite_uid = premium_invite_uid)

    if invited_profile.invited_friends.all().count() == 2 or not invited_profile.premium:

        return redirect('/register/')

    else:

        if request.method == 'POST':

            name = request.POST.get('n')

            username = request.POST.get('u')
            password = request.POST.get('p')

            user = User(username = username)
            user.set_password(password)
            user.save()

            user.profile.name = name
            user.profile.initials = ''.join(letter[0].upper() for letter in name.split(' '))[0:3]
            user.profile.premium = True
            user.profile.premium_since = dt.now()

            user.profile.invited_by = invited_profile
            invited_profile.invited_friends.add(user.profile)

            uid = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(7))

            while True:
                if Profile.objects.get(premium_invite_uid = uid).exists():
                    uid = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(7))
                else:
                    break

            user.profile.premium_invite_uid = uid
            user.profile.save()

            user = authenticate(username = username, password = password)
            login(request, user)

            return redirect('/home/')

        return render(request, 'auth/register.html')

def ce(request):

    e = request.POST.get('e')

    if User.objects.filter(username = e).exists():

        return JsonResponse({'u': 'n'})

    else:

        return JsonResponse({'u': 'y'})

@lr
def toggle_mode(request):

    request.user.profile.dark_mode = not request.user.profile.dark_mode
    request.user.profile.save()
    return HttpResponse('K')

""" Account changes """

@lr
def change_name(request):

    request.user.profile.name = request.POST.get('n')

    request.user.profile.initials = ''.join(letter[0].upper() for letter in request.POST.get('n').split(' '))[0:3]

    request.user.profile.save()

    return HttpResponse('K')

@lr
def change_username(request):

    request.user.username = request.POST.get('e')
    
    request.user.save()

    # already exists exception

    return HttpResponse('K')

@lr
def change_password(request):

    user = User(username = request.user.username)
    user.set_password(request.POST.get('p'))
    user.save()

    return HttpResponse('K')