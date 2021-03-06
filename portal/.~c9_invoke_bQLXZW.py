from django.conf.urls import url
from portal import views

urlpatterns = [
    # Server
    url(r'^/$', views.web_welcome, name='welcome'),
    url(r'^login/$', views.web_login, name='login'),
    url(r'^register/$', views.web_register, name='register'),
    url(r'^home/$', views.web_my_locks, name='home'),
    url(r'^logout/$', views.web_logout, name='logout'),
    url(r'^add-lock/$', views.web_add_lock, name='add-lock'),
    url(r'^share/(?P<lock_nickname>[\w|\W]+)/$', views.web_share, name='share'),
    url(r'^generate/(?P<lock_nickname>[\w|\W]+)/$', views.web_generate_code, name='generate'),
    url(r'^mechanic/(?P<lock_nickname>[\w|\W]+)/$', views.web_portal_mechanic, name='portal-mechanic'),
    url(r'^profile/$', views.web_profile, name='profile'),
    url(r'^about/$', views.web_about, name='about'),
    # Android
    url(r'^android/register/$', views.android_register),
    url(r'^android/login/$', views.android_login),
    url(r'^android/get_locks/$', views.android_locks_query),
    url(r'^android/verify_register/$', views.android_verify),
    url(r'^android/lock_mechanic/$', views.android_mechanic),
    url(r'^android/ping/$', views.android_ping),
    # Arduino
    url(r'^arduino/ping/$', views.arduino_mechanic),
]
