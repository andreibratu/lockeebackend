from django.contrib.auth.models import User
from django import forms
from .models import Lock


class UserReg(forms.ModelForm):
    username = forms.CharField(label='Your email')
    first_name = forms.CharField(label='Your name')
    password = forms.CharField(label='Choose a password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'password']


class UserLogin(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password']


class AndroLogin(forms.Form):
    username = forms.CharField()
    password = forms.CharField()

    class Meta:
        model = User
        fields = ['username', 'password']


class AddLock(forms.Form):
    lock_id = forms.CharField(label="Your Lockee's ID")
    nickname = forms.CharField(label='Give it a nickname')

    class Meta:
        model = Lock
        fields = ['lock_id', 'nickname', ]


class AndroRegister(forms.ModelForm):

    class Meta:
         model = User
         fields = ['username', 'first_name', 'password']

    username = forms.CharField()
    name = forms.CharField()
    password = forms.CharField()


class VerifyAndro(forms.Form):
    username = forms.CharField(label='username')


class LockWorker(forms.Form):
    username = forms.CharField()


class AndroidOpenLock(forms.Form):
    lock_inner_id = forms.CharField()
