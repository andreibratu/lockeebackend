from django.contrib.auth.models import User
from django import forms
from .models import Lock


class UserReg(forms.Form):
    usermail = forms.EmailField()
    name = forms.CharField()
    password = forms.CharField()


class UserLogin(forms.Form):
    usermail = forms.EmailField()
    password = forms.CharField()



class AndroidLogin(forms.Form):
    username = forms.CharField()
    password = forms.CharField()


class AddLock(forms.Form):
    lockcode = forms.CharField()
    lockname = forms.CharField()


class AndroidRegister(forms.Form):
    username = forms.CharField()
    name = forms.CharField()
    password = forms.CharField()


class VerifyAndroid(forms.Form):
    username = forms.CharField(label='username')


class AndroidGetLocks(forms.Form):
    username = forms.CharField()


class AndroidOpenLock(forms.Form):
    lock_inner_id = forms.CharField()


class AndroidAddLock(forms.Form):
    username = forms.CharField()
    lock_inner_id = forms.CharField()
    nickname = forms.CharField() 