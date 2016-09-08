from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, datetime

class LockAbsVal(models.Model):
    lockInnerID = models.CharField(max_length=30)
    isOpened = models.BooleanField(default=True)
    orientation = models.CharField(max_length=5, default='left')

    def __str__(self):
        return self.lockInnerID
        
    def statusCheck(self):
        if self.orientation == 'left':
            if self.isOpened:
                return '#unlocked'
            else:
                return '#locked'
        else:
            if self.isOpened:
                return '#locked'
            else:
                return '#unlocked'
    
    def updateDoorStatus(self):
        if self.orientation == 'left':
            if self.isOpened:
                self.isOpened = False
                self.save()
                return '#locked'
            else:
                self.isOpened = True
                self.save()
                return '#unlocked'
        else:
            if self.isOpened:
                self.isOpened = False
                self.save()
                return '#unlocked'
            else:
                self.isOpened = True
                self.save()
                return '#locked'



class Lock(models.Model):
    nickname = models.CharField(max_length=30, default='')
    staticShareID = models.CharField(max_length=30, default='')
    sessionShareID = models.CharField(max_length=30, default='')
    bindedAbsoluteLock = models.ForeignKey(LockAbsVal, on_delete=models.CASCADE)
    sessionExpire = models.DateTimeField(default=timezone.now)
    sessionExpireReadable = models.CharField(default='', max_length=50)
    
    def __str__(self):
        return self.nickname
        
    def shareIDStillAvailable(self):
        if timezone.now() < self.sessionExpire:
            return True
        else:
            return False
    
    def generateStaticShareID(self):
        from random import choice
        from string import ascii_uppercase
        self.staticShareID = ''
        for i in range(0, 11):
            self.staticShareID += choice(ascii_uppercase)
        self.save()
        
    def generateSessionShareID(self, timeDeltaDictionary):
        from random import choice
        from string import ascii_uppercase
        difference = timedelta(days=timeDeltaDictionary['days'], hours=timeDeltaDictionary['hours'], minutes=timeDeltaDictionary['minutes'])
        self.sessionShareID = ''
        for i in range(0, 11):
            self.sessionShareID += choice(ascii_uppercase)
        self.sessionExpire = timezone.now() + difference
        difference = timedelta(days=timeDeltaDictionary['days'], hours=timeDeltaDictionary['hours']+3, minutes=timeDeltaDictionary['minutes'])
        displayDate = timezone.now() + difference
        self.sessionExpireReadable = displayDate.strftime('%e %B %Y %H:%M')
        self.save()
    

class Owner(models.Model):
    bindedAbsoluteUser = models.OneToOneField(User)
    bindedRelativeLocks = models.ManyToManyField(Lock)

    def __str__(self):
        return self.bindedAbsoluteUser
