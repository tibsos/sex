from django.shortcuts import render, redirect, HttpResponse, get_object_or_404

from django.core.mail import send_mail
from django.conf import settings
from uuid import uuid4

from django.contrib.auth import authenticate, login

from django.contrib.auth.models import User
from .models import Profile

def forgot_password(request):
    return render(request, 'auth/forgot-password.html')

def send_recovery_email(request):

    email = request.POST.get('e')

    try:
        user = User.objects.get(username = email)

        token = uuid4()

        user.profile.password_recovery_token = token
        user.profile.save()

        subject = 'Восстановление пароля от вашего Блокнотика'
        message = f'Здравствуйте, {user.profile.name}!\n\nПожалуйста, перейдите по этой ссылке, чтобы установить новый пароль: https://bloknot-ik.ru/reset-password/{token}/\n\nС уважением,\nКоманда Блокнотика'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [user.username]
        send_mail(subject, message, email_from, recipient_list)

        return HttpResponse('K')

    except:
        return HttpResponse('N')

def reset_password(request, password_recovery_token):

    profile = get_object_or_404(Profile, password_recovery_token = password_recovery_token)

    if request.method == 'POST':

        profile.password_recovery_token = None
        profile.save()

        subject = 'Пароль от вашего Блокнотика изменен'
        message = f'Здравствуйте, {profile.name}!\n\nПароль от вашего Блокнотика только что поменяли.\nЕсли это были не вы, пожалуйста, сообщите нам об этом по этому адресу.\n\nС уважением,\nКоманда Блокнотика'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [profile.user.username]
        send_mail(subject, message, email_from, recipient_list)

        new_password = request.POST.get('p')

        profile.user.set_password(new_password)

        user = authenticate(

            username = profile.user.username,

            password = new_password

        )

        login(request, user)

        return redirect('/home/')

    return render(request, 'auth/reset-password.html')