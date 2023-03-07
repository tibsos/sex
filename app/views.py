from django.shortcuts import render, HttpResponse, redirect

from django.contrib.auth.decorators import login_required as lr

from datetime import datetime as dt
from datetime import timezone

from django.contrib.auth.models import User

from .models import *

import time
from uuid import uuid4 as u4
from yookassa import Configuration, Payment

from django.views.decorators.csrf import csrf_exempt

Configuration.account_id = 982702
Configuration.secret_key = 'test_klohaQM6zuhTIcPhup-xnT4erKZ8dYNyohfA4sWkB2A'

""" PAYMENT """

@lr
@csrf_exempt
def pay(request):

    payment = Payment.create({
        "amount": {
            "value": "100.00",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "http://158.160.48.112:8181/home/"
        },
        "capture": True,
        "description": f"{request.user.pk}", 
    }, u4())
    
    while True:

        if request.method == 'POST':
            print(request)
            break
        else:
            time.sleep(1)

    # get post request from UM
        # verify that ure the recipient

    return HttpResponse('K')

""" APP """

max_folders = 1
max_notes = 3

@lr
def app(request):

    folders = Folder.objects.filter(author = request.user)
    notes = Note.objects.filter(author = request.user).filter(deleted = False).filter(archived = False)

    user_premium = request.user.profile.premium
    
    c = {}

    if user_premium:
        c['max_notes'] = False
        c['max_notepads'] = False
    else: 
        if len(notes) >= max_notes:
            c['max_notes'] = True
        else:
            c['max_notes'] = False

        if len(folders) >= max_folders:
            c['max_notepads'] = True
        else:
            c['max_notepads'] = False

    if user_premium and not request.user.profile.premium_friend_offer_shown:
        c['first_friend_offer'] = True

        request.user.profile.premium_friend_offer_shown = True
        request.user.profile.save()
    else:
        c['first_friend_offer'] = False

    if request.user.profile.invited_friends.all().count() < 2 and user_premium and not request.user.profile.invited_by:
        c['friend_offer'] = True
    else:
        c['friend_offer'] = False 

    c['user'] = request.user
    c['profile'] = request.user.profile
    c['premium'] = request.user.profile.premium

    c['home'] = True

    c['pinned_notes'] = notes.filter(pinned = True)
    c['other_notes'] = notes.filter(pinned = False)

    c['folders'] = folders

    return render(request, 'home.html', c)


# Note sections

@lr
def home(request):

    notes = Note.objects.filter(author = request.user).filter(deleted = False).filter(archived = False)

    c = {}

    c['home'] = True

    c['pinned_notes'] = notes.filter(pinned = True)
    c['other_notes'] = notes.filter(pinned = False)

    return render(request, 'components/notes.html', c)

@lr
def loved(request):

    notes = Note.objects.filter(author = request.user).filter(deleted = False).filter(archived = False).filter(loved = True)
    
    c = {}

    c['loved'] = True

    c['pinned_notes'] = notes.filter(pinned = True)
    c['other_notes'] = notes.filter(pinned = False)

    return render(request, 'components/notes.html', c)

@lr
def archive(request):

    notes = Note.objects.filter(author = request.user).filter(deleted = False).filter(archived = True)
    
    c = {}

    c['archive'] = True

    c['pinned_notes'] = notes.filter(pinned = True)
    c['other_notes'] = notes.filter(pinned = False)

    return render(request, 'components/notes.html', c)

@lr
def trash(request):
    
    c = {}

    c['trash'] = True

    notes = list(Note.objects.filter(author = request.user).filter(deleted = True))

    for note in notes:

        difference = dt.now(timezone.utc) - note.deleted_at

        if difference.total_seconds() > 604800:

            notes.remove(note)
            note.delete()

    c['deleted_notes'] = notes

    return render(request, 'components/notes.html', c)

# Folder functionality

@lr
def create_folder(request):

    Folder.objects.create(

        author = request.user,

        title = request.POST.get('t'),

    )

    return render(request, 'components/folders.html', {'folders': Folder.objects.filter(author = request.user)})

@lr
def get_folder(request, uid):

    folder = Folder.objects.get(uid = uid)

    notes = Note.objects.filter(folders__in = [folder]).filter(deleted = False).filter(archived = False)

    c = {}

    c['folder'] = folder

    c['pinned_notes'] = notes.filter(pinned = True)
    c['other_notes'] = notes.filter(pinned = False)

    return render(request, 'components/notes.html', c)

@lr
def edit_folder(request):

    folder = Folder.objects.get(uid = request.POST.get('u'))
    folder.title = request.POST.get('t')
    folder.save()

    return HttpResponse('K')

@lr
def delete_folder(request):

    Folder.objects.get(uid = request.POST.get('f')).delete()

    return render(request, 'components/folders.html', {'folders': Folder.objects.filter(author = request.user)})

@lr
def get_note(request, uid):
    return render(request, 'components/current-note.html', {'note': Note.objects.get(uid = uid)})

@lr
def add_folder(request):

    folder = Folder.objects.get(uid = request.POST.get('f'))
    note = Note.objects.get(uid = request.POST.get('n'))

    note.folders.add(folder)

    return HttpResponse('K')

@lr
def remove_folder(request):

    note = Note.objects.get(uid = request.POST.get('n'))

    note.folders.remove(Folder.objects.get(uid = request.POST.get('f')))

    return HttpResponse('K')

# Note functionality

@lr
def create_note(request):

    note_loved = request.POST.get('l')
    note_pinned = request.POST.get('p')

    if note_loved == 'on':
        note_loved = True
    else:
        note_loved = False

    if note_pinned == 'on':
        note_pinned = True
    else:
        note_pinned = False

    note = Note.objects.create(

        author = request.user,

        title = request.POST.get('t'),
        content = request.POST.get('c'),

        loved = note_loved,
        pinned = note_pinned,

    )

    # Folders

    folders = request.POST.get('b')

    if folders:

        folders = folders.split(' ')
    
        for folder in folders:

            note.folders.add(Folder.objects.get(uid = folder))

    c = {}

    # Determining the section to return notes 

    folder_section = request.POST.get('f')
    love_section = request.POST.get('ls')
    archive_section = request.POST.get('as')

    if love_section == 'on':
        love_section = True
    else:
        love_section = False

    if archive_section == 'on':
        archive_section = True
    else:
        archive_section = False

    if love_section:
        notes = Note.objects.filter(author = request.user).filter(deleted = False).filter(archived = False).filter(loved = True)
        c['pinned_notes'] = notes.filter(pinned = True)
        c['other_notes'] = notes.filter(pinned = False)
        c['loved'] = True
    elif len(folder_section) != 0:
        notes = Note.objects.filter(author = request.user).filter(deleted = False).filter(archived = False).filter(folders__in = [Folder.objects.get(uid = folder_section)])
        c['pinned_notes'] = notes.filter(pinned = True)
        c['other_notes'] = notes.filter(pinned = False)
        c['folder'] = Folder.objects.get(uid = folder_section)
    elif archive_section:
        notes = Note.objects.filter(author = request.user).filter(deleted = False).filter(archived = True)
        c['pinned_notes'] = notes.filter(pinned = True)
        c['other_notes'] = notes.filter(pinned = False)
        c['archive'] = True
    else:
        notes = Note.objects.filter(author = request.user).filter(deleted = False).filter(archived = False)
        c['pinned_notes'] = notes.filter(pinned = True)
        c['other_notes'] = notes.filter(pinned = False)
        c['home'] = True

    return render(request, 'components/notes.html', c)

# Search notes

@lr
def search_notes(request):

    c = {}
    c['search'] = True

    # Process search request

    query = request.POST.get('q')

        # Note section booleans
    folder = request.POST.get('f')
    love = request.POST.get('l')
    archive = request.POST.get('a')
    trash = request.POST.get('t')

        # Processing
    if love == 'on':
        love = True
    else:
        love = False

    if archive == 'on':
        archive = True
    else:
        archive = False

    if trash == 'on':
        trash = True
    else:
        trash = False

    if query == '':
        if love:
            notes = Note.objects.filter(author = request.user).filter(deleted = False).filter(archived = False).filter(loved = True)
        elif archive:
            notes = Note.objects.filter(author = request.user).filter(deleted = False).filter(archived = True)
        elif trash:
            notes = Note.objects.filter(author = request.user).filter(deleted = True)
        elif len(folder) != 0:
            notes = Note.objects.filter(author = request.user).filter(deleted = False).filter(archived = False).filter(folders__in = [Folder.objects.get(uid = folder)])
        else:
            notes = Note.objects.filter(author = request.user).filter(deleted = False).filter(archived = False)

    else:
        if love:
            notes1 = list(Note.objects.filter(author = request.user).filter(deleted = False).filter(archived = False).filter(loved = True).filter(title__contains = query))
            notes2 = list(Note.objects.filter(author = request.user).filter(deleted = False).filter(archived = False).filter(loved = True).filter(content__contains = query))
            notes = set(notes1 + notes2)
        elif archive:
            notes1 = list(Note.objects.filter(author = request.user).filter(deleted = False).filter(archived = True).filter(title__contains = query))
            notes2 = list(Note.objects.filter(author = request.user).filter(deleted = False).filter(archived = True).filter(content__contains = query))
            notes = set(notes1 + notes2)
        elif trash:
            notes1 = list(Note.objects.filter(author = request.user).filter(deleted = True).filter(title__contains = query))
            notes2 = list(Note.objects.filter(author = request.user).filter(deleted = True).filter(content__contains = query))
            notes = set(notes1 + notes2)
        elif len(folder) != 0:
            notes1 = list(Note.objects.filter(author = request.user).filter(deleted = False).filter(archived = False).filter(folders__in = [Folder.objects.get(uid = folder)]).filter(title__contains = query))
            notes2 = list(Note.objects.filter(author = request.user).filter(deleted = False).filter(archived = False).filter(folders__in = [Folder.objects.get(uid = folder)]).filter(content__contains = query))
            notes = set(notes1 + notes2)
        else:
            notes1 = list(Note.objects.filter(author = request.user).filter(deleted = False).filter(archived = False).filter(title__contains = query))
            notes2 = list(Note.objects.filter(author = request.user).filter(deleted = False).filter(archived = False).filter(content__contains = query))
            notes = set(notes1 + notes2)

    c['found_notes'] = notes

    print(folder)

    if len(folder) != 0:
        c['folder'] = Folder.objects.get(uid = folder)
    elif love:
        c['loved'] = True
    elif archive:
        c['archive'] = True
    elif trash:
        c['trash'] = True
    else:
        c['home'] = True

    return render(request, 'components/notes.html', c)

@lr
def cancel_search(request):

    c = {}

        # Note section booleans
    folder = request.POST.get('f')
    love = request.POST.get('l')
    archive = request.POST.get('a')
    trash = request.POST.get('t')

        # Processing
    if love == 'on':
        love = True
    else:
        love = False

    if archive == 'on':
        archive = True
    else:
        archive = False

    if trash == 'on':
        trash = True
    else:
        trash = False

        # Note returns
    if love:
        notes = Note.objects.filter(author = request.user).filter(deleted = False).filter(archived = False).filter(loved = True)
        c['pinned_notes'] = notes.filter(pinned = True)
        c['other_notes'] = notes.filter(pinned = False)
    elif archive:
        notes = Note.objects.filter(author = request.user).filter(deleted = False).filter(archived = True)
        c['pinned_notes'] = notes.filter(pinned = True)
        c['other_notes'] = notes.filter(pinned = False)
    elif trash:
        c['deleted_notes'] = Note.objects.filter(author = request.user).filter(deleted = True)
    elif len(folder) != 0:
        notes = Note.objects.filter(author = request.user).filter(deleted = False).filter(archived = False).filter(folders__in = [Folder.objects.get(uid = folder)])
        c['pinned_notes'] = notes.filter(pinned = True)
        c['other_notes'] = notes.filter(pinned = False)
    else:
        notes = Note.objects.filter(author = request.user).filter(deleted = False).filter(archived = False)
        c['pinned_notes'] = notes.filter(pinned = True)
        c['other_notes'] = notes.filter(pinned = False)

    if len(folder) != 0:
        c['folder'] = Folder.objects.get(uid = folder)
    elif love:
        c['loved'] = True
    elif archive:
        c['archive'] = True
    elif trash:
        c['trash'] = True
    else:
        c['home'] = True

    return render(request, 'components/notes.html', c)

# Photos

@lr
def upload_photo_to_note(request):

    note = Note.objects.get(uid = request.POST.get('i'))

    photo = Photo.objects.create(

        uploader = request.user,
        note = note,
        file = request.FILES.get('p'),

    )

    note.photos.add(photo)

    return render(request, 'components/current-note-photos.html', {'photos': note.photos.all()})

@lr
def delete_photo(request):

    photo = Photo.objects.get(uid = request.POST.get('p'))
    note = Note.objects.get(uid = request.POST.get('n'))

    note.photos.remove(photo)
    photo.delete()

    return HttpResponse('K')


# Note actions

@lr
def love_note(request):

    note = Note.objects.get(uid = request.POST.get('n'))
    note.loved = not note.loved
    note.save()

    return HttpResponse('K')

@lr
def pin_note(request):

    note = Note.objects.get(uid = request.POST.get('n'))
    note.pinned = not note.pinned
    note.save()

    return HttpResponse('K')

@lr
def archive_note(request):

    note = Note.objects.get(uid = request.POST.get('n'))
    note.archived = not note.archived
    note.save()

    return HttpResponse('K')

@lr
def delete_note(request):

    note = Note.objects.get(uid = request.POST.get('n'))
    note.deleted = not note.deleted
    note.save()

    return HttpResponse('K')

# Note content updates

@lr
def update_contents(request):

    note = Note.objects.get(uid = request.POST.get('u'))

    note.title = request.POST.get('t')
    note.content = request.POST.get('c')
    note.save()

    return HttpResponse('K')

@lr
def update_title(request):

    note = Note.objects.get(uid = request.POST.get('u'))
    note.title = request.POST.get('t')
    note.save()

    return HttpResponse('K')

@lr
def update_content(request):

    note = Note.objects.get(uid = request.POST.get('u'))
    note.content = request.POST.get('c')
    note.save()

    return HttpResponse('K')


# Trash
@lr
def empty_trash(request):

    notes = list(Note.objects.filter(author = request.user).filter(deleted = True))

    for note in notes:

        note.delete()

    return HttpResponse('k')