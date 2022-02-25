from django.urls import path
from . import views
from .views import *


urlpatterns = [
	path('', home,name='home'),
	path('user_signup', user_signup,name='user_signup'),
	# path('user_login', user_login,name='user_login'),
	path('change_password', change_password,name='change_password'),
	path('user_logout', user_logout,name='user_logout'),
	path('data_owner_dashboard', data_owner_dashboard,name='data_owner_dashboard'),
	path('admin_dashboard', data_owner_dashboard,name='admin_dashboard'),
	path('user_list', user_list,name='user_list'),
	path('approve_user/<int:id>', approve_user, name='approve_user'),
]
