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



class AndroLogin(forms.Form):
    username = forms.CharField()
    password = forms.CharField()


class AddLock(forms.Form):
    lockcode = forms.CharField()
    lockname = forms.CharField()


class AndroRegister(forms.ModelForm):
    username = forms.CharField()
    name = forms.CharField()
    password = forms.CharField()


class VerifyAndro(forms.Form):
    username = forms.CharField(label='username')


class LockWorker(forms.Form):
    username = forms.CharField()


class AndroidOpenLock(forms.Form):
    lock_inner_id = forms.CharField()
