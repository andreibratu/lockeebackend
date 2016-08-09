from django.conf.urls import url
from portal import views

urlpatterns = [
    # Server
    url(r'^login/$', views.Login.as_view(), name='login'),
    url(r'^register/$', views.Register.as_view(), name='register'),
    url(r'^my-locks/$', views.Display_My_Locks.as_view(), name='my-locks'),
    url(r'^logout/$', views.log_out, name='logout'),
    url(r'^add-lock/$', views.Add_Lock.as_view(), name='add-lock'),
    url(r'^share/(?P<lock_nickname>[\w|\W]+)/$', views.share, name='share'),
    url(r'^generate/(?P<lock_nickname>[\w|\W]+)/$', views.generate_code, name='generate'),
    url(r'^mechanic/(?P<lock_nickname>[\w|\W]+)/$', views.portal_mechanic, name='portal-mechanic'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^about/$', views.about, name='about'),
    # Android
    url(r'^android/register/$', views.android_register),
    url(r'^android/login/$', views.android_login),
    url(r'^android/get_locks/$', views.android_locks_query),
    url(r'^android/verify_register/$', views.android_verify),
    url(r'^android/lock_mechanic/$', views.android_mechanic),
    # Arduino
    url(r'^arduino/ping/$', views.arduino_mechanic, name='arduino-register-lock'),
]
