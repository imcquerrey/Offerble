from django.urls import include, path
from django.urls import re_path as url
from django.views.generic.base import RedirectView
from . import views
app_name = 'main'
handler404 = 'main.views.handler404'
urlpatterns = [
	path('', views.index, name='index'),
	path('login', views.login, name='login'),
	path('register', views.register, name='register'),
	path('dashboard', views.dashboard, name='dashboard'),
	path('active', views.activeoffers, name='activeoffers'),
	path('reports', views.reports, name='reports'),
	path('edit', views.edit, name='edit'),
	path('postback', views.postback, name='postback'),
	path('offerwalls', views.apps, name='apps'),
	path('payments', views.payments, name='payments'),
	path('privacy', views.privacy, name='privacy'),
	path('profile', views.profile, name='profile'),
	path('wall', views.wall, name='index'),
	path('qreset', views.qreset, name='qreset'),
	path('history', views.history, name='history'),
	path('logout', views.logout, name='logout'),
	path('offer-direct', views.offer_direct, name='offer_direct'),
	path('reset_password/', views.reset_password, name='reset_password'),
	url(r'^m/(?P<id1>\w{0,5})$', views.mobile, name='mobile'),
	url(r'^favicon\.ico$', RedirectView.as_view(url='/static/imgs/favicon.ico')),
	url(r'^media/(?P<loc>\w+)/(?P<inside>\w+)/(?P<name>[-\w.]+)$', views.renderMedia),
	path('send', views.send, name='send'),

	path('adgate', views.adgate, name='adgate'),
	path('adgem', views.adgem, name='adgem'),
	path('toro', views.toro, name='toro'),
	path('ayet', views.ayet, name='ayet'),
]




