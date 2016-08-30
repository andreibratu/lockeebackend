from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.list import ListView
from random import choice
from string import ascii_uppercase
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View
from forms import ShareIDOpen, UserReg, UserLogin, AddLock, VerifyAndroid, AndroidOpenLock, AndroidGetLocks, AndroidLogin, AndroidRegister, AndroidAddLock, AndroidGenerateCode
from django.contrib.auth.mixins import LoginRequiredMixin
from portal.models import Owner, LockAbsVal, Lock
from django.shortcuts import render_to_response
from django.template import RequestContext
import json


# SERVER SIDE ####



def handler404(request):
    response = render_to_response('portal/404.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 404
    return response


def handler500(request):
    response = render_to_response('portal/500.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 500
    return response


def web_welcome(request):
    """This view displays the welcome page."""
    if request.user.is_authenticated():
        return redirect('portal:home')
    return render(request, 'portal/welcome.html', {})


def web_register(request):
    """This view handles the register requests on the web client."""
    form_class = UserReg
    register_form = form_class(request.POST)
    
    if request.method == 'POST':
        if register_form.is_valid():
            new_user = User()
            username = register_form.cleaned_data['usermail']
            password = register_form.cleaned_data['password']
            name = register_form.cleaned_data['name']
            try:
                duplicate_check = User.objects.get(username = username)
                return render(request, 
                    'portal/welcome.html', {'error': 'Username already registered'})
            except User.DoesNotExist:
                new_user.username = username
                new_user.set_password(password)
                new_user.first_name = name
                new_user.save()
                new_owner = Owner(owner = new_user)
                new_owner.save()
                user = authenticate(username=username, password=password)
                login(request, user)
                return redirect('portal:home')
        else:
            return render(request, 'portal/welcome.html', {'error': 'Invalid register form'})
    else:
        return render(request, 'portal/forbidden.html', {})
        

def web_login(request):
    """This view handles the login request on the web client."""
    form_class = UserLogin
    login_form = form_class(request.POST)
    
    if request.method == 'POST':
        if login_form.is_valid():
            username = login_form.cleaned_data['usermail']
            password = login_form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('portal:home')
                else:
                    return render(request, 'portal/welcome.html', {'error': 'Inactive user'})
            else:
                return render(request, 'portal/welcome.html', {'error': 'Invalid credentials'})
        else:
            return render(request, 'portal/welcome.html', {'error': 'Invalid login form'}) 
    else:
        return render(request, 'portal/forbidden.html', {})


@login_required(login_url='portal:welcome')
def web_display_locks(request, message=''):
    what_owner = Owner.objects.get(owner=request.user)
    locks_of_logged_in_user = what_owner.locks.all()
    return render(request, 'portal/home.html', {'object_list': locks_of_logged_in_user, 'error': message})


@login_required(login_url='portal:welcome')
def web_add_lock(request):
    """This function submits the form for DB processing."""
    form_class = AddLock
    form = form_class(request.POST)
    
    if request.method == 'POST':
        if form.is_valid():
            error=''
            lock_inner_id = form.cleaned_data['lockcode']
            nickname = form.cleaned_data['lockname']
            orientation = form.cleaned_data['orientation']
            owner = Owner.objects.get(owner=request.user)
            try:
                abs_lock = LockAbsVal.objects.get(lock_inner_id=lock_inner_id)
                try:
                    lock_already_added = owner.locks.get(abs_lock=abs_lock)
                    error = 'You have already added this lock'
                except Lock.DoesNotExist:
                    try:
                        nickname_already_used = owner.locks.get(nickname=nickname)
                        error = 'You have already used this nickname'
                    except Lock.DoesNotExist:
                        abs_lock.orientation = orientation
                        abs_lock.save()
                        new_lock = Lock(abs_lock=abs_lock, nickname=nickname)
                        new_lock.save()
                        owner.locks.add(new_lock)
                        owner.save()
                        return web_display_locks(request, message='Lock added sucessfully')
            except LockAbsVal.DoesNotExist:
                error = 'The Lock Does Not Exist'
            return web_display_locks(request, error)
        else:
            return HttpResponse('bad form')
    else:
        return render(request, 'portal/forbidden.html', {})


@login_required(login_url='portal:login')
def web_logout(request):
    """This view logs the user out."""
    logout(request)
    return render(request, 'portal/welcome.html', {})


@login_required(login_url='portal:login')
def web_generate_code(request, lock_nickname):
    """This view generates a new share code at user's demand."""
    logged_in_owner = Owner.objects.get(owner=request.user)
    lock_to_change = logged_in_owner.locks.get(nickname=lock_nickname)
    lock_to_change.share_id = ''
    for i in range(0, 11):
        lock_to_change.share_id += choice(ascii_uppercase)
    lock_to_change.save()
    logged_in_owner.save()
    message = "Here's the new share code for %s" % lock_nickname
    return web_display_locks(request, message)


@login_required(login_url='portal:login')
def web_profile(request):
    """This view handles the user's profile on the web site."""
    return render(request, 'portal/profile.html', {'name': request.user.first_name})


def web_about(request):
    """This view presents the details of this project's godlike developers."""
    return render(request, 'portal/about.html', {})


@login_required(login_url='portal:login')
def web_portal_mechanic(request, lock_inner_id, lock_nickname):
    """This view opens/closes a lock via the website."""
    what_lock = LockAbsVal.objects.get(lock_inner_id=lock_inner_id)
    if what_lock.is_opened:
        what_lock.is_opened = False
        message = "%s is now closed" % lock_nickname
        what_lock.save()
        return web_display_locks(request, message)
    else:
        what_lock.is_opened = True
        message = "%s is now opened" % lock_nickname
        what_lock.save()
        return web_display_locks(request, message)
    return HttpResponse('something bad happened')


@login_required(login_url='portal:login')
def web_delete_lock(request, nickname):
    """This view deletes a relative_lock from the owner's list."""
    owner = Owner.objects.get(owner=request.user)
    owner.locks.get(nickname=nickname).delete()
    message = "%s has been removed from the list" % nickname
    return web_display_locks(request, message)


# ANDROID SIDE ###

@csrf_exempt
def android_login(request):
    """This view handles the login requests that come from the android terminal."""
    if request.method == 'POST':
        form = AndroidLogin(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                return HttpResponse('login success')
            else:
                return HttpResponse('fail')
        else:
            return HttpResponse('Form Error')
    else:
        return render(request, 'portal/forbidden.html', {})


@csrf_exempt
def android_register(request):
    """This view handles the register requests that come from the an android terminal."""
    if request.method == 'POST':
        form = AndroidRegister(request.POST)
        if form.is_valid():
            new_user = User()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            full_name = form.cleaned_data['name']
            new_user.username = username
            new_user.set_password(password)
            new_user.first_name = full_name
            new_user.save()
            create_owner = Owner(owner=new_user)
            create_owner.save()
            return HttpResponse('register success')
        else:
            return HttpResponse('form fail')
    else:
        return render(request, 'portal/forbidden.html', {})


@csrf_exempt
def android_verify(request):
    """This view helps the android terminal check username availability in real time."""
    if request.method == 'POST':
        
        form = VerifyAndroid(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                User.objects.get(username=username)
                return HttpResponse('email already taken')
            except User.DoesNotExist:
                return HttpResponse('verify success')
        else:
            return HttpResponse('wow')
    else:
        return render(request, 'portal/forbidden.html', {})


@csrf_exempt
def android_mechanic(request):
    """This view opens/closes a lock via an android terminal."""
    if request.method == 'POST':
        form = AndroidOpenLock(request.POST)
        if form.is_valid():
            lock_inner_id = form.cleaned_data['lock_inner_id']
            try:
                what_lock = LockAbsVal.objects.get(lock_inner_id=lock_inner_id)
                if what_lock.is_opened:
                    what_lock.is_opened = False
                    response = 'locked'
                else:
                    what_lock.is_opened = True
                    response = 'unlocked'
                what_lock.save()
                return HttpResponse(response)
            except LockAbsVal.DoesNotExist:
                return HttpResponse(lock_inner_id)
        else:
            return HttpResponse('bad form')
    else:
        return render(request, 'portal/forbidden.html', {})


@csrf_exempt
def android_locks_query(request):
    """This view sends to the android terminal the locks the user has access to."""
    if request.method == 'POST':
        form = AndroidGetLocks(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                logged_user = User.objects.get(username=username)
                logged_owner = Owner.objects.get(owner=logged_user)
                try:
                    user_locks = logged_owner.locks.all()
                    lock_info = {'locks_info': [{'nickname': lock.nickname, 'lock_inner_id': lock.abs_lock.lock_inner_id, 'share_id': lock.share_id, 'status': lock.abs_lock.is_opened} for lock in user_locks]}
                    json_response = json.dumps(lock_info)
                    return HttpResponse(json_response)
                except Lock.DoesNotExist:
                    return HttpResponse('0')
            except User.DoesNotExist:
                return HttpResponse('unknown user')
        else:
            return HttpResponse('form error')
    else:
        return render(request, 'portal/forbidden.html', {})


@csrf_exempt
def android_ping(request):
    """This lets the Android client ping the server to try server connection."""
    if request.method == 'GET':
        return HttpResponse('received')
    else:
        return render(request, 'portal/forbidden.html', {})
    
    
@csrf_exempt
def android_add_lock(request):
    """Allows the android terminal to add a lock into the DB."""
    if request.method == "POST":
        form = AndroidAddLock(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            lock_inner_id = form.cleaned_data['lock_inner_id']
            nickname = form.cleaned_data['nickname']
            orientation = form.cleaned_data['orientation']
            the_user = User.objects.get(username=username)
            try:
                lock_validity = LockAbsVal.objects.get(lock_inner_id=lock_inner_id)
                try:
                    owner = Owner.objects.get(owner=the_user)
                    try:
                        duplicate_nickname_check = owner.locks.get(nickname=nickname)
                        return HttpResponse('nickname already used')
                    except Lock.DoesNotExist:
                        abs_lock = LockAbsVal.objects.get(lock_inner_id=lock_inner_id)
                        try:
                            abs_lock_already_added_check = owner.locks.get(abs_lock=abs_lock)
                            return HttpResponse('this lock was already registered')
                        except Lock.DoesNotExist:
                            abs_lock.orientation = orientation
                            abs_lock.save()
                            new_lock = Lock(abs_lock=abs_lock, nickname=nickname)
                            new_lock.save()
                            owner.locks.add(new_lock)
                            owner.save()
                            return HttpResponse('lock registered')
                except User.DoesNotExist:
                    return HttpResponse('user does not exist')
            except LockAbsVal.DoesNotExist:
                return HttpResponse('lock does not exist')
        else:
            return HttpResponse('invalid form')
    else:
        return render(request, 'portal/forbidden.html', {})


@csrf_exempt
def android_generate_code(request):
    """This view generates a new share code at user's demand on android terminal."""
    if request.method == 'POST':
        form = AndroidGenerateCode(request.POST)
        if form.is_valid():
            nickname = form.cleaned_data['nickname']
            username = form.cleaned_data['username']
            what_user = User.objects.get(username=username)
            logged_in_owner = Owner.objects.get(owner=what_user)
            lock_to_change = logged_in_owner.locks.get(nickname=nickname)
            lock_to_change.share_id = ''
            for i in range(0, 11):
                lock_to_change.share_id += choice(ascii_uppercase)
            lock_to_change.save()
            logged_in_owner.save()
            return HttpResponse(lock_to_change.share_id)
        else:
            return HttpResponse('bad form')
    else:
        return render(request, 'portal/forbidden.html', {})
    

@csrf_exempt
def android_profile(request):
    """This view helps the android terminal to get the fullname of the user."""
    if request.method == 'POST':
        form = VerifyAndroid(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            full_name = User.first_name
            try:
                User.objects.get(username=username)
                return HttpResponse(full_name)
            except User.DoesNotExist:
                return HttpResponse('user does not exist')
        else:
            return HttpResponse('wow')
    else:
       return render(request, 'portal/forbidden.html', {})
    
    
@csrf_exempt
def android_remove(request):
    """Allows removal of locks from android terminal."""
    if request.method == 'POST':
        form = AndroidGenerateCode(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            nickname = form.cleaned_data['nickname']
            try:
                what_user = User.objects.get(username=username)
                owner = Owner.objects.get(owner=what_user)
                try:
                    owner.locks.get(nickname=nickname).delete()
                    return HttpResponse('success')
                except Lock.DoesNotExist:
def android_open_sharecode(request)
            except User.DoesNotExist:
                return HttpResponse('user error')
        else:
            return HttpResponse('bad form')
    else:
        return render(request, 'portal/forbidden.html', {})
    

@csrf_exempt
def android_open_sharecode(request):
    """Allows an android terminal to unlock the door by share_id."""
    if request.method == 'POST':
        form = ShareIDOpen(request.POST)
        if form.is_valid():
            shareID = form.cleaned_data['shareID']
            try:
                what_lock = Lock.objects.get(share_id=shareID)
                if what_lock.abs_lock.is_opened:
                    what_lock.abs_lock.is_opened = False
                    what_lock.save()
                    return HttpResponse('closed')
                else:
                    what_lock.abs_lock.is_opened = True
                    what_lock.save()
                    return HttpResponse('opened')
            except Lock.DoesNotExist:
                return HttpResponse('bad code')
    else:
        return render(request, 'portal/forbidden.html', {})


# ARDUINO SIDE
@csrf_exempt
def arduino_mechanic(request):
    """This view is pinged by the arduino clients to check for changes in db ( every 1 sec )"""
    if request.method == 'POST':
        lock_inner_id = request.body
        try:
            already_registered_lock = LockAbsVal.objects.get(lock_inner_id=lock_inner_id)
            is_opened = already_registered_lock.is_opened
            if is_opened:
                return HttpResponse('#unlocked')
            else:
                return HttpResponse('#locked')
        except LockAbsVal.DoesNotExist:
            new_registration_lock = LockAbsVal(lock_inner_id=lock_inner_id)
            new_registration_lock.save()
            return HttpResponse('new lock registered')
    else:
        return render(request, 'portal/forbidden.html', {})