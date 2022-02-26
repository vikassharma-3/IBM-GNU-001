from django.urls import path
from . import views
from .views import *


urlpatterns = [
	path('', home,name='home'),
	path('user_signup', user_signup,name='user_signup'),
	path('change_password', change_password,name='change_password'),
	path('user_logout', user_logout,name='user_logout'),
	path('user_dashboard', user_dashboard,name='user_dashboard'),
	path('admin_dashboard', admin_dashboard,name='admin_dashboard'),
	path('manage_user', manage_user,name='manage_user'),
	path('approve_user/<int:id>', approve_user, name='approve_user'),
	path('delete_user/<int:id>', delete_user, name='delete_user'),
	path('deactivate_user/<int:id>', deactivate_user, name='deactivate_user'),
	path('clear_notification', clear_notification, name='clear_notification'),
]
