from django.conf.urls import url
from portal import views

urlpatterns = [
    # Server
    url(r'^$', views.webWelcome, name='welcome'),
    url(r'^login/$', views.webLogin, name='login'),
    url(r'^register/$', views.webRegister, name='register'),
    url(r'^home/$', views.webDisplayLocks, name='home'),
    url(r'^logout/$', views.webLogout, name='logout'),
    url(r'^add-lock/$', views.webAddLock, name='add-lock'),
    url(r'^generate_static/(?P<lockNickname>[\w|\W]+)/$', views.webGenerateStaticShareID, name='generate-static'),
    url(r'^generate_session/(?P<lockNickname>[\w|\W]+)/$', views.webGenerateSessionShareID, name='generate-session'),
    url(r'^mechanic/(?P<lockInnerID>[\w|\W]+)/(?P<lockNickname>[\w|\W]+)/$', views.webMechanic, name='portal-mechanic'),
    url(r'^profile/$', views.webProfile, name='profile'),
    url(r'^about/$', views.webAbout, name='about'),
    url(r'^delete/(?P<nickname>[\w|\W]+)/$', views.webDeleteLock, name='delete'),
    # Android
    url(r'^android/register/$', views.androidRegister),
    url(r'^android/login/$', views.androidLogin),
    url(r'^android/get_locks/$', views.androidLocksQuery),
    url(r'^android/verify_register/$', views.androidVerifyUsername),
    url(r'^android/lock_mechanic/$', views.androidMechanic),
    url(r'^android/add_lock/$', views.androidAddLock),
    url(r'^android/ping/$', views.androidPing),
    url(r'^android/generate_static/$', views.androidGenerateStaticShareID),
    url(r'^android/generate_session/$', views.androidGenerateSessionShareID),
    url(r'^android/remove/$', views.androidRemove),
    url(r'^android/share_mechanic/$', views.androidShareMechanic),
    url(r'^android/share_check/$', views.androidShareCheck),
    url(r'^android/share_details/$', views.androidShareDetails),
    url(r'^android/share_mechanic/$', views.androidShareMechanic),
    url(r'^android/get_session/$', views.androidQueryLockSession),
    url(r'^android/get_details/$', views.androidLockDetails),
    # Arduino
    url(r'^arduino/ping/$', views.arduinoMechanic,),
]
