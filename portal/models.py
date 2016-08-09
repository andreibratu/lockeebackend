from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User


class LockAbsVal(models.Model):
    lock_inner_id = models.CharField(max_length=30)
    is_opened = models.BooleanField(default=True)

    def __str__(self):
        return self.lock_inner_id


class Lock(models.Model):
    nickname = models.CharField(max_length=30, default='')
    share_id = models.CharField(max_length=30, default='')
    abs_lock = models.ForeignKey(LockAbsVal, on_delete=models.CASCADE)

    def __str__(self):
        return self.nickname


class Owner(models.Model):
    owner = models.OneToOneField(User)
    locks = models.ManyToManyField(Lock)

    def __str__(self):
        return self.owner
