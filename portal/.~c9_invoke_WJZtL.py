from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.list import ListView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View
from forms import WebGenerateSessionShareID, ShareIDOpen, UserReg, UserLogin, AddLock, VerifyAndroid, AndroidOpenLock, AndroidGetLocks, AndroidLogin, AndroidRegister, AndroidAddLock, AndroidBasicInfo, AndroidGenerateSessionShareID
from django.contrib.auth.mixins import LoginRequiredMixin
from portal.models import Owner, LockAbsVal, Lock
from django.shortcuts import render_to_response
from django.template import RequestContext
import json
from datetime import datetime, date


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
            form_username = register_form.cleaned_data['usermail']
            form_password = register_form.cleaned_data['password']
            form_name = register_form.cleaned_data['name']
            try:
                duplicate_user_check = User.objects.get(username=form_username)
                return render(request, 'portal/welcome.html', {'error': 'Username already registered'})
            except User.DoesNotExist:
                new_user = User(username=form_username, first_name=form_name)
                new_user.set_password(form_password)
                new_user.save()
                new_owner = Owner(abs_user_binding=new_user).save(0)
                auth_user = authenticate(username=form_username, password=form_password)
                login(request, auth_user)
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
            form_username = login_form.cleaned_data['usermail']
            form_password = login_form.cleaned_data['password']
            auth_user = authenticate(username=form_username, password=form_password)
            if auth_user is not None:
                login(request, auth_user)
                return redirect('portal:home')
            else:
                return render(request, 'portal/welcome.html', {'error': 'Invalid credentials'})
        else:
            return render(request, 'portal/welcome.html', {'error': 'Invalid login form'}) 
    else:
        return render(request, 'portal/forbidden.html', {})


@login_required(login_url='portal:welcome')
def web_display_locks(request, message=''):
    what_owner = Owner.objects.get(abs_user_binding=request.user)
    locks_of_logged_in_user = what_owner.binded_locks.all()
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
            new_orientation = form.cleaned_data['orientation']
            owner = Owner.objects.get(abs_user_binding=request.user)
            try:
                abs_lock = LockAbsVal.objects.get(lock_inner_id=lock_inner_id)
                try:
                    lock_already_added = owner.binded_locks.get(binded_abs_lock=abs_lock)
                    error = 'You have already added this lock'
                except Lock.DoesNotExist:
                    try:
                        nickname_already_used = owner.binded_locks.get(nickname=nickname)
                        error = 'You have already used this nickname'
                    except Lock.DoesNotExist:
                        abs_lock.orientation = new_orientation
                        abs_lock.save()
                        new_lock = Lock(binded_abs_lock=abs_lock, nickname=nickname)
                        new_lock.save()
                        owner.binded_locks.add(new_lock)
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
def web_generate_static_code(request, lock_nickname):
    """This view generates a new static share code at user's demand."""
    logged_in_owner = Owner.objects.get(abs_user_binding=request.user)
    lock_to_change = logged_in_owner.binded_locks.get(nickname=lock_nickname)
    lock_to_change.generate_static_shareid()
    message = "Here's the new static share code for %s" % lock_to_change.nickname
    return web_display_locks(request, message)


@login_required(login_url='portal:login')
def web_generate_session_code(request, lock_nickname):
    """This view generates a new session share code at user's demand."""
    if request.method == 'POST':
        form = WebGenerateSessionShareID(request.POST)
        if form.is_valid():
            form_days = form.cleaned_data['days']
            form_hours = form.cleaned_data['hours']
            form_minutes = form.cleaned_data['minutes']
            
            logged_in_owner = Owner.objects.get(abs_user_binding=request.user)
            lock_to_change = logged_in_owner.binded_locks.get(nickname=lock_nickname)
            time_diff_dict = {'days': int(form_days), 'hours': int(form_hours), 'minutes': int(form_minutes)}
            lock_to_change.generate_session_shareid(time_diff_dict)
            message = "Here's the new session share code for %s" % lock_to_change.nickname
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
    lock_to_be_updated = LockAbsVal.objects.get(lock_inner_id=lock_inner_id)
    result = lock_to_be_updated.update_door_status()
    message = "%s is now %s" % (lock_nickname, result)
    return web_display_locks(request, message)


@login_required(login_url='portal:login')
def web_delete_lock(request, nickname):
    """This view deletes a relative_lock from the owner's list."""
    owner = Owner.objects.get(abs_user_binding=request.user)
    owner.binded_locks.get(nickname=nickname).delete()
    message = "%s has been removed from the list" % nickname
    return web_display_locks(request, message)


# ANDROID SIDE ###

@csrf_exempt
def android_login(request):
    """This view handles the login requests that come from the android terminal."""
    if request.method == 'POST':
        form = AndroidLogin(request.POST)
        if form.is_valid():
            form_username = form.cleaned_data['username']
            form_password = form.cleaned_data['password']
            user = authenticate(username=form_username, password=form_password)
            if user is not None:
                return HttpResponse('login success')
            else:
                return HttpResponse('fail')
        else:
            return HttpResponse('bad form')
    else:
        return render(request, 'portal/forbidden.html', {})


@csrf_exempt
def android_register(request):
    """This view handles the register requests that come from the an android terminal."""
    if request.method == 'POST':
        form = AndroidRegister(request.POST)
        if form.is_valid():
            form_username = form.cleaned_data['username']
            form_password = form.cleaned_data['password']
            form_name = form.cleaned_data['name']
            new_user = User(username=form_username, first_name=form_name)
            new_user.set_password(form_password)
            new_user.save()
            new_owner = Owner(abs_user_binding=new_user).save()
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
            form_username = form.cleaned_data['username']
            try:
                User.objects.get(username=form_username)
                return HttpResponse('email already taken')
            except User.DoesNotExist:
                return HttpResponse('verify success')
        else:
            return HttpResponse('bad form')
    else:
        return render(request, 'portal/forbidden.html', {})


@csrf_exempt
def android_mechanic(request):
    """This view opens/closes a lock via an android terminal."""
    if request.method == 'POST':
        form = AndroidOpenLock(request.POST)
        if form.is_valid():
            form_lock_inner_id = form.cleaned_data['lock_inner_id']
            try:
                lock_to_be_updated = LockAbsVal.objects.get(lock_inner_id=form_lock_inner_id)
                return HttpResponse(lock_to_be_updated.update_door_status())
            except LockAbsVal.DoesNotExist:
                return HttpResponse("lock does not exist")
        else:
            return HttpResponse('bad form')
    else:
        return render(request, 'portal/forbidden.html', {})


@csrf_exempt
def android_locks_query(request):
    """This view is used to query the DB for an user's locks from an android terminal."""
    if request.method == 'POST':
        form = AndroidGetLocks(request.POST)
        if form.is_valid():
            form_username = form.cleaned_data['username']
            try:
                logged_user = User.objects.get(username=form_username)
                logged_owner = Owner.objects.get(abs_user_binding=logged_user)
                try:
                    list_locks = logged_owner.binded_locks.all()
                    lock_info = {'locks_info': [{'nickname': lock.nickname, 'lock_inner_id': lock.binded_abs_lock.lock_inner_id, 'share_id': lock.static_share_id, 'status': lock.binded_abs_lock.is_opened} for lock in list_locks]}
                    json_response = json.dumps(lock_info)
                    return HttpResponse(json_response)
                except Lock.DoesNotExist:
                    return HttpResponse('lock does not exist')
            except User.DoesNotExist:
                return HttpResponse('user does not exist')
        else:
            return HttpResponse('bad form')
    else:
        return render(request, 'portal/forbidden.html', {})


@csrf_exempt
def android_ping(request):
    """View used by Android terminal to check server status."""
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
            form_username = form.cleaned_data['username']
            form_lock_inner_id = form.cleaned_data['lock_inner_id']
            form_nickname = form.cleaned_data['nickname']
            form_orientation = form.cleaned_data['orientation']
            try:
                lock_validity = LockAbsVal.objects.get(lock_inner_id=form_lock_inner_id)
                try:
                    owner = Owner.objects.get(abs_user_binding=User.objects.get(username=form_username))
                    try:
                        duplicate_nickname_check = owner.binded_locks.get(nickname=form_nickname)
                        return HttpResponse('nickname already used')
                    except Lock.DoesNotExist:
                        abs_lock = LockAbsVal.objects.get(lock_inner_id=form_lock_inner_id)
                        try:
                            abs_lock_already_added_check = owner.binded_locks.get(binded_abs_lock=abs_lock)
                            return HttpResponse('this lock was already registered')
                        except Lock.DoesNotExist:
                            abs_lock.orientation = form_orientation
                            abs_lock.save()
                            new_lock = Lock(binded_abs_lock=abs_lock, nickname=form_nickname)
                            new_lock.save()
                            owner.binded_locks.add(new_lock)
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
def android_generate_session_shareid(request):
    """This view generates a new share code at user's demand on android terminal."""
    if request.method == 'POST':
        form = AndroidGenerateSessionShareID(request.POST)
        if form.is_valid():
            form_nickname = form.cleaned_data['nickname']
            form_username = form.cleaned_data['username']
            form_days = form.cleaned_data['days']
            form_hours = form.cleaned_data['hours']
            form_minutes = form.cleaned_data['minutes']
            logged_in_owner = Owner.objects.get(abs_user_binding=User.objects.get(username=form_username))
            lock_to_change = logged_in_owner.binded_locks.get(nickname=form_nickname)
            time_diff_dict = {'days': int(form_days), 'hours': int(form_hours), 'minutes': int(form_minutes)}
            response = {'session_share_id': lock_to_change.session_share_id, 'ex}
            expiration_date = lock_to_change.session_expire.strftime('%A:%B:%Y:')
            response = {'session_share_info': {'session_share_id': lock_to_change.session_share_id, 'expiration_date': expiration_date}}
            response = json.dumps(response)
            return HttpResponse(response)
        else:
            return HttpResponse('bad form')
    else:
        return render(request, 'portal/forbidden.html', {})
        
        
@csrf_exempt
def android_generate_static_shareid(request):
    if request.method == 'POST':
        form = AndroidBasicInfo(request.POST)
        if form.is_valid():
            form_nickname = form.cleaned_data['nickname']
            form_username = form.cleaned_data['username'
            ]
            logged_in_owner = Owner.objects.get(abs_user_binding=User.objects.get(username=form_username))
            lock_to_change = logged_in_owner.binded_locks.get(nickname=form_nickname)
            lock_to_change.generate_static_shareid()
            return HttpResponse(lock_to_change.static_share_id)
        else:
            return HttpResponse('bad form')
    else:
        return render(request, 'portal/forbiden.html', {})

@csrf_exempt
def android_profile(request):
    """This view helps the android terminal to get the fullname of the user."""
    if request.method == 'POST':
        form = VerifyAndroid(request.POST)
        if form.is_valid():
            form_username = form.cleaned_data['username']
            try:
                return HttpResponse(User.objects.get(username=form_username).first_name)
            except User.DoesNotExist:
                return HttpResponse('user does not exist')
        else:
            return HttpResponse('bad_form')
    else:
       return render(request, 'portal/forbidden.html', {})
    

@csrf_exempt
def android_remove(request):
    """Allows removal of locks from android terminal."""
    if request.method == 'POST':
        form = AndroidBasicInfo(request.POST)
        if form.is_valid():
            form_username = form.cleaned_data['username']
            form_nickname = form.cleaned_data['nickname']
            try:
                owner = Owner.objects.get(abs_user_binding=User.objects.get(username=form_username))
                try:
                    owner.binded_locks.get(nickname=form_nickname).delete()
                    return HttpResponse('success')
                except Lock.DoesNotExist:
                    return HttpResponse('lock does not exist')
            except User.DoesNotExist:
                return HttpResponse('user does not exist')
        else:
            return HttpResponse('bad form')
    else:
        return render(request, 'portal/forbidden.html', {})
    
    
@csrf_exempt
def android_share_code(request):
    """Checks share_id sent by android terminal."""
    if request.method == 'POST':
        form = ShareIDOpen(request.POST)
        if form.is_valid():
            form_share_id = form.cleaned_data['shareID']
            try:
                queried_lock = Lock.objects.get(share_id=form_share_id)
                if queried_lock.is_session_share_id:
                    if queried_lock.shareid_still_available():
                        return HttpResponse(queried_lock.nickname)
            except Lock.DoesNotExist:
                return HttpResponse('wrong code')
        else:
            return HttpResponse('bad form')
    else:
        return render(request, 'portal/forbidden.html', {})
        
@csrf_exempt
def android_share_ping(request):
    """Returns a lock's status to android terminal."""
    if request.method == 'POST':
        form = ShareIDOpen(request.POST)
        if form.is_valid():
            shareID = form.cleaned_data['shareID']
            try:
                queried_lock = Lock.objects.get(share_id=shareID)
                return HttpResponse(queried_lock.status_check())
            except Lock.DoesNotExist:
                return HttpResponse('wrong code')
        else:
            return HttpResponse('bad form')
    else:
        return render(request, 'portal/forbidden.html', {})


@csrf_exempt
def android_share_mechanic(request):
    """Allows an android terminal to unlock the door by share_id."""
    if request.method == 'POST':
        form = ShareIDOpen(request.POST)
        if form.is_valid():
            form_share_id = form.cleaned_data['shareID']
            queried_lock = Lock.objects.get(share_id=form_share_id)
            return HttpResponse(queried_lock.update_door_status())
        else:
            return HttpResponse('bad form')
    else:
        return render(request, 'portal/forbidden.html', {})


# ARDUINO SIDE
@csrf_exempt
def arduino_mechanic(request):
    """This view is pinged by the arduino clients to check for changes in the model."""
    if request.method == 'POST':
        lock_inner_id = request.body
        try:
            queried_abs_lock = LockAbsVal.objects.get(lock_inner_id=lock_inner_id)
            return HttpResponse(queried_abs_lock.status_check())
        except LockAbsVal.DoesNotExist:
            new_abs_lock = LockAbsVal(lock_inner_id=lock_inner_id).save()
            return HttpResponse('success')
    else:
        return render(request, 'portal/forbidden.html', {})