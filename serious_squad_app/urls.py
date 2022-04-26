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
	path('upload_data',upload_data,name='upload_data'),
	path('my_data',my_data,name='my_data'),
	path('delete_data/<int:id>', delete_data, name='delete_data'),
	path('download_data/<path>/<data>', download_data, name='download_data'),
	path('list_data', list_data, name='list_data'),
	path('request_data/<int:id>', request_data, name='request_data'),
	path('manage_data_request', manage_data_request, name='manage_data_request'),
	path('approve_data_request/<int:id>', approve_data_request, name='approve_data_request'),
	path('reject_data_request/<int:id>', reject_data_request, name='reject_data_request'),
	path('revoke_data_permission/<int:id>', revoke_data_permission, name='revoke_data_permission'),
	path('list_user_data', list_user_data, name='list_user_data'),
	path('flagged_data', flagged_data, name='flagged_data'),
	path('report_flag', report_flag, name='report_flag'),
	path('remove_flag/<int:id>', remove_flag, name='remove_flag'),
	path('delete_inappropriate/<int:id>', delete_inappropriate, name='delete_inappropriate'),
	path('list_user_activity', list_user_activity, name='list_user_activity'),
	path('clear_logs',clear_logs,name='clear_logs'),
	path('about',about,name='about'),
]
