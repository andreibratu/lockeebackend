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
from forms import UserReg, UserLogin, AddLock, VerifyAndro, AndroidOpenLock, LockWorker
from django.contrib.auth.mixins import LoginRequiredMixin
from portal.models import Owner, LockAbsVal, Lock
from portal.forms import AndroLogin, AndroRegister
import json


# SERVER SIDE ####


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
        return render(request, 'portal/error.html', 
            {'title': 'Forbidden', 'error': 'You are not supposed to be here ^_^'})
        

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
        return render(request, 'portal/error.html', 
            {'title': 'Forbidden', 'error': 'You are not supposed to be here ^_^'})


class Display_My_Locks(LoginRequiredMixin, ListView):
    """This view displays the locks of the logged in user."""
    login_url = 'portal:welcome'
    redirect_field_name = 'redirect_to'
    template_name = 'portal/home.html'

    def get_queryset(self):
        locks_of_logged_in_user = Owner.objects.get(owner=self.request.user)
        return locks_of_logged_in_user.locks.all()


@login_required(login_url='portal:welcome')
def web_add_lock(request):
    """This function submits the form for DB processing."""
    form_class = AddLock
    form = form_class(request.POST)
    
    if request.method == 'POST':
        if form.is_valid():
            lock_id = form.cleaned_data['lockcode']
            new_lock_nickname = form.cleaned_data['lockname']
            owner = Owner.objects.get(owner=request.user)
            absolute_lock = LockAbsVal.objects.get(lock_inner_id=lock_id)
            try:
                owner.locks.get(abs_lock=absolute_lock)
                return render(request, 'portal/welcome.html', {'error': 'Lock already added'})
            except Lock.DoesNotExist:
                new_relative_lock = Lock()
                new_relative_lock.nickname = new_lock_nickname
                new_relative_lock.abs_lock = absolute_lock
                new_relative_lock.save()
                owner.locks.add(new_relative_lock)
                owner.save()
                return redirect('portal:home')
        else:
            return HttpResponse('Form error')
    else:
        return render(request, 'portal/error.html',
          {'title': 'Forbidden', 'message': 'You are not supposed to be here ^_^'})


@login_required(login_url='portal:login')
def web_logout(request):
    """This view logs the user out."""
    logout(request)
    return render(request, 'portal/logout.html', {})


@login_required(login_url='portal:login')
def web_share(request, lock_nickname):
    """This view redirects the user to the share menu of a lock."""
    logged_in_owner = Owner.objects.get(owner=request.user)
    lock_to_be_shared = logged_in_owner.locks.get(nickname=lock_nickname)
    return render(request, 'portal/share.html', {'what_lock': lock_to_be_shared})


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
    return redirect(reverse('portal:share', kwargs={'lock_nickname': lock_to_change.nickname}))


@login_required(login_url='portal:login')
def web_profile(request):
    """This view handles the user's profile on the web site."""
    return render(request, 'portal/profile.html', {'name': request.user.first_name})


def web_about(request):
    """This view presents the details of this project's godlike developers."""
    return render(request, 'portal/about.html', {})


@login_required(login_url='portal:login')
def web_portal_mechanic(request, lock_inner_id):
    """This view opens/closes a lock via the website."""
    owner = Owner.objects.get(owner=request.user)
    what_lock = owner.locks.abs_lock.objects.get(lock_inner_id=lock_inner_id)
    if what_lock.is_opened:
        what_lock.is_opened = False
        message = "%s is now closed" % what_lock.nickname
        what_lock.save()
    else:
        what_lock.is_opened = True
        message = "%s is now opened" % what_lock.nickname
        what_lock.save()
    return render(request, 'portal/my-locks.html', {'message': message})



# ANDROID SIDE ###


@csrf_exempt
def android_login(request):
    """This view handles the login requests that come from the android terminal."""
    if request.method == 'POST':
        form = AndroLogin(request.POST)
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
        return render(request, 'portal/error.html',
                      {'title': 'Forbidden', 'message': 'You are not supposed to be here ^_^'})


@csrf_exempt
def android_register(request):
    """This view handles the register requests that come from the an android terminal."""
    if request.method == 'POST':
        form = AndroRegister(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
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
        return render(request, 'portal/error.html',
                      {'title': 'Forbidden', 'message': 'You are not supposed to be here ^_^'})


@csrf_exempt
def android_verify(request):
    """This view helps the android terminal check username availability in real time."""
    if request.method == 'POST':
        form = VerifyAndro(request.POST)
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
        return render(request, 'portal/error.html',
                      {'title': 'Forbidden', 'message': 'You are not supposed to be here ^_^'})


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
        return render(request, 'portal/error.html',
                      {'title': 'Forbidden', 'message': 'You are not supposed to be here ^_^'})


@csrf_exempt
def android_locks_query(request):
    """This view sends to the android terminal the locks the user has access to."""
    if request.method == 'POST':
        form = LockWorker(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                logged_user = User.objects.get(username=username)
                logged_owner = Owner.objects.get(owner=logged_user)
                try:
                    user_locks = logged_owner.locks.all()
                    lock_info = {'locks_info': [{'nickname': lock.nickname, 'share_id': lock.share_id, 'is_opened': lock.abs_lock.is_opened} for lock in user_locks]}
                    json_response = json.dumps(lock_info)
                    return HttpResponse(json_response)
                except Lock.DoesNotExist:
                    return HttpResponse('0')
            except User.DoesNotExist:
                return HttpResponse('unknown user')
        else:
            return HttpResponse('form error')
    else:
        return render(request, 'portal/error.html',
                      {'title': 'Forbidden', 'message': 'You are not supposed to be here ^_^'})


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
                return HttpResponse('#unlock')
            else:
                return HttpResponse('#locked')
        except LockAbsVal.DoesNotExist:
            new_registration_lock = LockAbsVal(lock_inner_id=lock_inner_id)
            new_registration_lock.save()
            return HttpResponse('new lock registered')
    else:
        return render(request, 'portal/error.html',
                      {'title': 'Forbidden', 'message': 'You are not supposed to be here ^_^'})
