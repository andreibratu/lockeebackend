from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.list import ListView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View
from forms import AndroidDetails, WebGenerateSessionShareID, ShareIDOpen, UserReg, UserLogin, AddLock, VerifyAndroid, AndroidOpenLock, AndroidGetLocks, AndroidLogin, AndroidRegister, AndroidAddLock, AndroidBasicInfo, AndroidGenerateSessionShareID
from django.contrib.auth.mixins import LoginRequiredMixin
from portal.models import Owner, LockAbsVal, Lock
from django.shortcuts import render_to_response
from django.template import RequestContext
import json
from django.utils import timezone


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


def webWelcome(request):
    """This view displays the welcome page."""
    if request.user.is_authenticated():
        return redirect('portal:home')
    return render(request, 'portal/welcome.html', {})


def webRegister(request):
    """This view handles the register requests on the web client."""
    register_form = UserReg(request.POST)
    
    if request.method == 'POST':
        if register_form.is_valid():
            formUsername = register_form.cleaned_data['usermail']
            formPassword = register_form.cleaned_data['password']
            formName = register_form.cleaned_data['name']
            try:
                duplicateUserCheck = User.objects.get(username=formUsername)
                return render(request, 'portal/welcome.html', {'error': 'Username already registered'})
            except User.DoesNotExist:
                newUser = User(username=formUsername, first_name=formName)
                newUser.set_password(formPassword)
                newUser.save()
                newOwner = Owner(bindedAbsoluteUser=newUser).save(0)
                authUser = authenticate(username=formUsername, password=formPassword)
                login(request, authUser)
                return redirect('portal:home')
        else:
            return render(request, 'portal/welcome.html', {'error': 'Invalid register form'})
    else:
        return render(request, 'portal/forbidden.html', {})
        

def webLogin(request):
    """This view handles the login request on the web client."""
    form_class = UserLogin
    login_form = form_class(request.POST)
    
    if request.method == 'POST':
        if login_form.is_valid():
            formUsername = login_form.cleaned_data['usermail']
            formPassword = login_form.cleaned_data['password']
            authUser = authenticate(username=formUsername, password=formPassword)
            if authUser is not None:
                login(request, authUser)
                return redirect('portal:home')
            else:
                return render(request, 'portal/welcome.html', {'error': 'Invalid credentials'})
        else:
            return render(request, 'portal/welcome.html', {'error': 'Invalid login form'}) 
    else:
        return render(request, 'portal/forbidden.html', {})


@login_required(login_url='portal:welcome')
def webDisplayLocks(request, message=''):
    queriedOwner = Owner.objects.get(bindedAbsoluteUser=request.user)
    queriedUserLocks = queriedOwner.bindedRelativeLocks.all()
    return render(request, 'portal/home.html', {'object_list': queriedUserLocks, 'error': message})


@login_required(login_url='portal:welcome')
def webAddLock(request):
    """This function submits the form for DB processing."""
    form = AddLock(request.POST)
    
    if request.method == 'POST':
        if form.is_valid():
            error=''
            lockInnerID = form.cleaned_data['lockcode']
            nickname = form.cleaned_data['lockname']
            newOrientation = form.cleaned_data['orientation']
            queriedOwner = Owner.objects.get(bindedAbsoluteUser=request.user)
            try:
                queriedAbsoluteLock = LockAbsVal.objects.get(lockInnerID=lockInnerID)
                try:
                    lock_already_added = queriedOwner.bindedRelativeLocks.get(bindedAbsoluteLock=queriedAbsoluteLock)
                    error = 'You have already added this lock'
                except Lock.DoesNotExist:
                    try:
                        nickname_already_used = queriedOwner.bindedRelativeLocks.get(nickname=nickname)
                        error = 'You have already used this nickname'
                    except Lock.DoesNotExist:
                        queriedAbsoluteLock.orientation = newOrientation
                        queriedAbsoluteLock.save()
                        newRelativeLock = Lock(bindedAbsoluteLock=queriedAbsoluteLock, nickname=nickname)
                        newRelativeLock.save()
                        queriedOwner.bindedRelativeLocks.add(newRelativeLock)
                        return webDisplayLocks(request, message='Lock added sucessfully')
            except LockAbsVal.DoesNotExist:
                error = 'The Lock Does Not Exist'
            return webDisplayLocks(request, error)
        else:
            return HttpResponse('bad form')
    else:
        return render(request, 'portal/forbidden.html', {})


@login_required(login_url='portal:login')
def webLogout(request):
    """This view logs the user out."""
    logout(request)
    return render(request, 'portal/welcome.html', {})


@login_required(login_url='portal:login')
def webGenerateStaticShareID(request, lockNickname):
    """This view generates a new static share code at user's demand."""
    queriedOwner = Owner.objects.get(bindedAbsoluteUser=request.user)
    queriedLock = queriedOwner.bindedRelativeLocks.get(nickname=lockNickname)
    queriedLock.generateStaticShareID()
    message = "Here's the new static share code for %s" % queriedLock.nickname
    return webDisplayLocks(request, message)


@login_required(login_url='portal:login')
def webGenerateSessionShareID(request, lockNickname):
    """This view generates a new session share code at user's demand."""
    if request.method == 'POST':
        form = WebGenerateSessionShareID(request.POST)
        if form.is_valid():
            form_days = form.cleaned_data['days']
            form_hours = form.cleaned_data['hours']
            form_minutes = form.cleaned_data['minutes']
            
            queriedOwner = Owner.objects.get(bindedAbsoluteUser=request.user)
            queriedLock = queriedOwner.bindedRelativeLocks.get(nickname=lockNickname)
            timeDeltaDictionary = {'days': int(form_days), 'hours': int(form_hours), 'minutes': int(form_minutes)}
            queriedLock.generateSessionShareID(timeDeltaDictionary)
            message = "Here's the new session share code for %s" % queriedLock.nickname
            return webDisplayLocks(request, message)


@login_required(login_url='portal:login')
def webProfile(request):
    """This view handles the user's profile on the web site."""
    return render(request, 'portal/profile.html', {'name': request.user.first_name})


def webAbout(request):
    """This view presents the details of this project's godlike developers."""
    return render(request, 'portal/about.html', {})


@login_required(login_url='portal:login')
def webMechanic(request, lockInnerID, lockNickname):
    """This view opens/closes a lock via the website."""
    queriedLock = LockAbsVal.objects.get(lockInnerID=lockInnerID)
    result = queriedLock.updateDoorStatus()
    message = "%s is now %s" % (lockNickname, result)
    return webDisplayLocks(request, message)


@login_required(login_url='portal:login')
def webDeleteLock(request, nickname):
    """This view deletes a relative_lock from the queriedOwner's list."""
    queriedOwner = Owner.objects.get(bindedAbsoluteUser=request.user)
    queriedOwner.bindedRelativeLocks.get(nickname=nickname).delete()
    message = "%s has been removed from the list" % nickname
    return webDisplayLocks(request, message)


# ANDROID SIDE ###

@csrf_exempt
def androidLogin(request):
    """This view handles the login requests that come from the android terminal."""
    if request.method == 'POST':
        form = AndroidLogin(request.POST)
        if form.is_valid():
            formUsername = form.cleaned_data['username']
            formPassword = form.cleaned_data['password']
            user = authenticate(username=formUsername, password=formPassword)
            if user is not None:
                return HttpResponse('login success')
            else:
                return HttpResponse('fail')
        else:
            return HttpResponse('bad form')
    else:
        return render(request, 'portal/forbidden.html', {})


@csrf_exempt
def androidRegister(request):
    """This view handles the register requests that come from the an android terminal."""
    if request.method == 'POST':
        form = AndroidRegister(request.POST)
        if form.is_valid():
            formUsername = form.cleaned_data['username']
            formPassword = form.cleaned_data['password']
            formName = form.cleaned_data['name']
            newUser = User(username=formUsername, first_name=formName)
            newUser.set_password(formPassword)
            newUser.save()
            newOwner = Owner(bindedAbsoluteUser=newUser)
            newOwner.save()
            return HttpResponse('register success')
        else:
            return HttpResponse('form fail')
    else:
        return render(request, 'portal/forbidden.html', {})


@csrf_exempt
def androidVerifyUsername(request):
    """This view helps the android terminal check username availability in real time."""
    if request.method == 'POST':
        form = VerifyAndroid(request.POST)
        if form.is_valid():
            formUsername = form.cleaned_data['username']
            try:
                User.objects.get(username=formUsername)
                return HttpResponse('email already taken')
            except User.DoesNotExist:
                return HttpResponse('verify success')
        else:
            return HttpResponse('bad form')
    else:
        return render(request, 'portal/forbidden.html', {})


@csrf_exempt
def androidMechanic(request):
    """This view opens/closes a lock via an android terminal."""
    if request.method == 'POST':
        form = AndroidOpenLock(request.POST)
        if form.is_valid():
            form_lockInnerID = form.cleaned_data['lockInnerID']
            try:
                queriedLock = LockAbsVal.objects.get(lockInnerID=form_lockInnerID)
                return HttpResponse(queriedLock.updateDoorStatus())
            except LockAbsVal.DoesNotExist:
                return HttpResponse("lock does not exist")
        else:
            return HttpResponse('bad form')
    else:
        return render(request, 'portal/forbidden.html', {})


@csrf_exempt
def androidLocksQuery(request):
    """This view is used to query the DB for an user's locks from an android terminal."""
    if request.method == 'POST':
        form = AndroidGetLocks(request.POST)
        if form.is_valid():
            formUsername = form.cleaned_data['username']
            try:
                queriedOwner = Owner.objects.get(bindedAbsoluteUser=User.objects.get(username=formUsername))
                try:
                    listLocks = queriedOwner.bindedRelativeLocks.all()
                    response = json.dumps({'locksInfo': [{'nickname': lock.nickname, 'lockInnerID': lock.bindedAbsoluteLock.lockInnerID, 'status': lock.bindedAbsoluteLock.isOpened} for lock in listLocks]})
                    return HttpResponse(response)
                except Lock.DoesNotExist:
                    return HttpResponse('lock does not exist')
            except User.DoesNotExist:
                return HttpResponse('user does not exist')
        else:
            return HttpResponse('bad form')
    else:
        return render(request, 'portal/forbidden.html', {})


@csrf_exempt
def androidPing(request):
    """View used by Android terminal to check server status."""
    if request.method == 'GET':
        return HttpResponse('received')
    else:
        return render(request, 'portal/forbidden.html', {})
    
    
@csrf_exempt
def androidAddLock(request):
    """Allows the android terminal to add a lock into the DB."""
    if request.method == "POST":
        form = AndroidAddLock(request.POST)
        if form.is_valid():
            formUsername = form.cleaned_data['username']
            form_lockInnerID = form.cleaned_data['lockInnerID']
            formNickname = form.cleaned_data['nickname']
            form_orientation = form.cleaned_data['orientation']
            try:
                lock_validity = LockAbsVal.objects.get(lockInnerID=form_lockInnerID)
                try:
                    queriedOwner = Owner.objects.get(bindedAbsoluteUser=User.objects.get(username=formUsername))
                    try:
                        duplicateNicknameCheck = queriedOwner.bindedRelativeLocks.get(nickname=formNickname)
                        return HttpResponse('nickname already used')
                    except Lock.DoesNotExist:
                        queriedAbsoluteLock = LockAbsVal.objects.get(lockInnerID=form_lockInnerID)
                        try:
                            queriedAbsoluteLock_already_added_check = queriedOwner.bindedRelativeLocks.get(bindedAbsoluteLock=queriedAbsoluteLock)
                            return HttpResponse('this lock was already registered')
                        except Lock.DoesNotExist:
                            queriedAbsoluteLock.orientation = form_orientation
                            queriedAbsoluteLock.save()
                            newRelativeLock = Lock(bindedAbsoluteLock=queriedAbsoluteLock, nickname=formNickname)
                            newRelativeLock.save()
                            queriedOwner.bindedRelativeLocks.add(newRelativeLock)
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
def androidGenerateSessionShareID(request):
    """This view generates a new share code at user's demand on android terminal."""
    if request.method == 'POST':
        form = AndroidGenerateSessionShareID(request.POST)
        if form.is_valid():
            formNickname = form.cleaned_data['nickname']
            formUsername = form.cleaned_data['username']
            formDays = form.cleaned_data['days']
            formHours = form.cleaned_data['hours']
            formMinutes = form.cleaned_data['minutes']
            queriedOwner = Owner.objects.get(bindedAbsoluteUser=User.objects.get(username=formUsername))
            queriedLock = queriedOwner.bindedRelativeLocks.get(nickname=formNickname)
            timeDeltaDictionary = {'days': int(formDays), 'hours': int(formHours), 'minutes': int(formMinutes)}
            queriedLock.generateSessionShareID(timeDeltaDictionary)
            response = {'sessionShareInfo': [{'sessionShareID': queriedLock.sessionShareID, 'sessionExpire': queriedLock.sessionExpireReadable}]}
            response = json.dumps(response)
            return HttpResponse(response)
        else:
            return HttpResponse('bad form')
    else:
        return render(request, 'portal/forbidden.html', {})
        
        
@csrf_exempt
def androidGenerateStaticShareID(request):
    if request.method == 'POST':
        form = AndroidBasicInfo(request.POST)
        if form.is_valid():
            formNickname = form.cleaned_data['nickname']
            formUsername = form.cleaned_data['username']
            queriedOwner = Owner.objects.get(bindedAbsoluteUser=User.objects.get(username=formUsername))
            queriedLock = queriedOwner.bindedRelativeLocks.get(nickname=formNickname)
            queriedLock.generateStaticShareID()
            return HttpResponse(queriedLock.staticShareID)
        else:
            return HttpResponse('bad form')
    else:
        return render(request, 'portal/forbiden.html', {})

@csrf_exempt
def androidProfile(request):
    """This view helps the android terminal to get the fullname of the user."""
    if request.method == 'POST':
        form = VerifyAndroid(request.POST)
        if form.is_valid():
            formUsername = form.cleaned_data['username']
            try:
                return HttpResponse(User.objects.get(username=formUsername).first_name)
            except User.DoesNotExist:
                return HttpResponse('user does not exist')
        else:
            return HttpResponse('bad_form')
    else:
       return render(request, 'portal/forbidden.html', {})
    
@csrf_exempt
def androidLockDetails(request):
    """Basically a refresh."""
    if request.method == 'POST':
        form = AndroidDetails(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            formlockInnerID = form.cleaned_data['lockInnerID']
            try:
                queriedUser = Owner.objects.get(bindedAbsoluteUser=User.objects.get(username=username))
                queriedAbsLock = LockAbsVal.objects.get(lockInnerID=formlockInnerID)
                queriedRelativeLock = queriedUser.bindedRelativeLocks.get(bindedAbsoluteLock=queriedAbsLock)
                response = json.dumps({'lockDetails': [{'nickname': queriedRelativeLock.nickname, 'staticShareID': queriedRelativeLock.staticShareID, 'status': queriedRelativeLock.bindedA.statusCheck()}]})
                return HttpResponse(response)
            except Lock.DoesNotExist:
                return HttpResponse('bad id')
            except User.DoesNotExist:
                return HttpResponse('bad username')
        else:
            return HttpResponse('bad form')
    else:
        return render(request, 'portal/forbidden.html', {})


@csrf_exempt
def androidRemove(request):
    """Allows removal of locks from android terminal."""
    if request.method == 'POST':
        form = AndroidBasicInfo(request.POST)
        if form.is_valid():
            formUsername = form.cleaned_data['username']
            formNickname = form.cleaned_data['nickname']
            try:
                queriedOwner = Owner.objects.get(bindedAbsoluteUser=User.objects.get(username=formUsername))
                try:
                    queriedOwner.bindedRelativeLocks.get(nickname=formNickname).delete()
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
def androidQueryLockSession(request):
    """DB query for retrieving info ab a lock's session."""
    if request.method == 'POST':
        form = AndroidBasicInfo(request.POST)
        if form.is_valid():
            formUsername = form.cleaned_data['username']
            formNickname = form.cleaned_data['nickname']
            try:
                queriedOwner = Owner.objects.get(bindedAbsoluteUser = User.objects.get(username=formUsername))
                queriedLock = queriedOwner.bindedRelativeLocks.get(nickname=formNickname)
                if queriedLock.shareIDStillAvailable():
                    response = json.dumps({'sessionShareInfo': [{'sessionShareID': queriedLock.sessionShareID, 'sessionExpire': queriedLock.sessionExpireReadable}]})
                else:
                    response = json.dumps({'sessionShareInfo': [{'sessionShareID': 'Code has expired', 'sessionExpire': 'Expired'}]})
                    queriedLock.sessionShareID = ''
                    queriedLock.session_expire = None
                    queriedLock.save()
                return HttpResponse(response)
            except User.DoesNotExist:
                return HttpResponse('user does not exist')
            
    
@csrf_exempt
def androidShareDetails(request):
    """Initial staticShareID check queries by android terminal."""
    if request.method == 'POST':
        form = ShareIDOpen(request.POST)
        if form.is_valid():
            formShareID = form.cleaned_data['shareID']
            try:
                queriedLock = Lock.objects.get(staticShareID=formShareID)
                response = json.dumps({'lockDetails': [{'nickname': queriedLock.nickname, 'status': queriedLock.bindedAbsoluteLock.statusCheck()}]})
                return HttpResponse(response)
            except Lock.DoesNotExist:
                try:
                    queriedLock = Lock.objects.get(sessionShareID=formShareID)
                    if queriedLock.shareIDStillAvailable():
                        response = json.dumps({'lockDetails': [{'nickname': queriedLock.nickname, 'status': queriedLock.bindedAbsoluteLock.statusCheck()}]})
                        return HttpResponse(response)
                    else:
                        queriedLock.sessionShareID = ''
                        queriedLock.session_expire = None
                        queriedLock.save()
                        return HttpResponse('expired')
                except Lock.DoesNotExist:
                    return HttpResponse('wr')
        else:
            return HttpResponse('bad form')
    else:
        return render(request, 'portal/forbidden.html', {})


@csrf_exempt
def androidShareCheck(request):
    """Checks if a share ID exists or is still available."""
    if request.method == 'POST':
        form = ShareIDOpen(request.POST)
        if form.is_valid():
            formShareID = form.cleaned_data['shareID']
            try:
                queriedLock = Lock.objects.get(staticShareID=formShareID)
                return HttpResponse('success')
            except Lock.DoesNotExist:
                try:
                    queriedLock = Lock.objects.get(sessionShareID=formShareID)
                    if queriedLock.shareIDStillAvailable():
                        return HttpResponse('success')
                    else:
                        
                        queriedLock.sessionShareID = ''
                        queriedLock.session_expire = timezone.now()
                        queriedLock.save()
                        return HttpResponse('expired')
                except Lock.DoesNotExist:
                    return HttpResponse('wrong code')
        else:
            return HttpResponse('bad form')
    else:
        return render(request, 'portal/forbidden.html', {}) 


@csrf_exempt
def androidShareMechanic(request):
    """Allows an android terminal to unlock the door by shareID."""
    if request.method == 'POST':
        form = ShareIDOpen(request.POST)
        if form.is_valid():
            formShareID = form.cleaned_data['shareID']
            try:
                queriedLock = Lock.objects.get(staticShareID=formShareID)
                return HttpResponse(queriedLock.bindedAbsoluteLock.updateDoorStatus())
            except Lock.DoesNotExist:
                try:
                    queriedLock = Lock.objects.get(sessionShareID=formShareID)
                    if queriedLock.shareIDStillAvailable():
                        return HttpResponse(queriedLock.bindedAbsoluteLock.updateDoorStatus())
                    else:
                        queriedLock.sessionShareID = ''
                        queriedLock.session_expire = timezone.now()
                        queriedLock.save()
                        return HttpResponse('expired')
                except Lock.DoesNotExist:
                    return HttpResponse('wrong code')
        else:
            return HttpResponse('bad form')
    else:
        return render(request, 'portal/forbidden.html', {})


# ARDUINO SIDE
@csrf_exempt
def arduinoMechanic(request):
    """This view is pinged by the arduino clients to check for changes in the model."""
    if request.method == 'POST':
        lockInnerID = request.body
        try:
            queriedAbsoluteLock = LockAbsVal.objects.get(lockInnerID=lockInnerID)
            return HttpResponse(queriedAbsoluteLock.statusCheck())
        except LockAbsVal.DoesNotExist:
            newAbsoluteLock = LockAbsVal(lockInnerID=lockInnerID)
            newAbsoluteLock.save()
            return HttpResponse('success')
    else:
        return render(request, 'portal/forbidden.html', {})