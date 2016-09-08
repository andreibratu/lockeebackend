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
    orientation = forms.ChoiceField(widget=forms.RadioSelect(), choices=[('left', 'left'), ('right', 'right')])


class AndroidRegister(forms.Form):
    username = forms.CharField()
    name = forms.CharField()
    password = forms.CharField()


class VerifyAndroid(forms.Form):
    username = forms.CharField(label='username')


class AndroidGetLocks(forms.Form):
    username = forms.CharField()


class AndroidOpenLock(forms.Form):
    lockInnerID = forms.CharField()


class AndroidAddLock(forms.Form):
    username = forms.CharField()
    lockInnerID = forms.CharField()
    nickname = forms.CharField()
    orientation = forms.CharField()
    

class AndroidGenerateSessionShareID(forms.Form):
    username = forms.CharField()
    nickname = forms.CharField()
    days = forms.CharField()
    hours = forms.CharField()
    minutes = forms.CharField()
    

class AndroidBasicInfo(forms.Form):
    username = forms.CharField()
    nickname = forms.CharField()
    
    
class ShareIDOpen(forms.Form):
    shareID = forms.CharField()
    
    
class WebGenerateSessionShareID(forms.Form):
    days = forms.IntegerField()
    hours = forms.IntegerField()
    minutes = forms.IntegerField()
    

class AndroidDetails(forms.Form):
    username = forms.CharField()
    lockInnerID = forms.CharField()
