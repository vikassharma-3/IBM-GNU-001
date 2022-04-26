from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import *
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from serious_squad.settings import EMAIL_HOST_USER
from django.core.mail import send_mail
from notifications.signals import notify
from serious_squad.settings import *
from django.core.files.storage import FileSystemStorage
from wsgiref.util import FileWrapper
import mimetypes
from django.utils.encoding import smart_text
import subprocess,os,sys
import random
import string
import datetime,time
from django.utils import timezone
import threading
import base64
from .filters import *
from verify_email.email_handler import send_verification_email

def superuser_only(function):
    def _inner(request, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request,'403.html')
        return function(request, *args, **kwargs)
    return _inner

def home(request):
    title = ""
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return render(request, 'admin_dashboard.html')
        if request.user.is_superuser is False:
            return render(request, 'user_dashboard.html')
    return render(request, 'index.html')

def user_signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # user.is_active = False
            # user.save()
            send_verification_email(request, form)
            n_recipient = User.objects.get(id=1)
            n_sender = User.objects.get(id=user.id)
            n_message = f'User { user.username }({user.email}) created account'
            notify.send(sender=n_sender, recipient=n_recipient, verb='User Signup Alert',description=n_message)
            e_subject = f'User Signup Alert'
            e_message = f'Hi admin,\n\nUser {user.username}({user.email}) created account on IBADS'
            e_recepient = 'serioussquad.ibads@gmail.com'
            send_mail(e_subject,e_message, EMAIL_HOST_USER, [e_recepient], fail_silently = True)
            messages.success(request, f'Successfully created account for {user.username}, verify email to activate the account !!!')
            activity_obj = UserActivity(activity=f'Account created for {user.email}.')
            activity_obj.save()
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password is successfully updated. Try to login with new password ')
            logout(request)
            return redirect('user_login')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {
        'form': form
    })

@login_required
def user_logout(request):
    logout(request)
    return redirect('home')

def user_dashboard(request):
    if request.user.is_authenticated:
        return render(request, 'user_dashboard.html')
    else:
        return redirect('login')

@superuser_only
def admin_dashboard(request):
    if request.user.is_authenticated:
        return render(request, 'admin_dashboard.html')
    else:
        return redirect('login')

@superuser_only
def manage_user(request):
    users = User.objects.all().exclude(id=request.user.id)
    return render(request,"manage_user.html",{'users':users})

@superuser_only
def approve_user(request, id):
    user = User.objects.get(id=id)
    user.is_active = 1
    user.save()
    try:
        notification = Notification.objects.get(actor_object_id=id)
        notification.delete()
    except:
        pass
    return redirect("manage_user")

@superuser_only
def deactivate_user(request, id):
    user = User.objects.get(id=id)
    user.is_active = 0
    user.save()
    return redirect("manage_user")

@superuser_only
def delete_user(request, id):
    user = User.objects.get(id=id)
    user.delete()
    activity_obj = UserActivity(activity=f'User {user.username} removed.')
    activity_obj.save()
    try:
        notification = Notification.objects.get(actor_object_id=id)
        notification.delete()
    except:
        pass
    return redirect("manage_user")

@login_required
def clear_notification(request):
    notification = Notification.objects.filter(recipient_id=request.user.id)
    notification.delete()
    return redirect('home')

@login_required
def upload_data(request):
    date=datetime.datetime.now() + datetime.timedelta(days=1)
    date = date.strftime("%Y-%m-%dT%H:%M")
    users = User.objects.all()
    if request.method == 'POST':
        form = DataForm(request.POST, request.FILES,)
        if form.is_valid():
            fs=form.save(commit=False)
            fs.user_id = request.user.id
            fs.key = base64_encode(generate_key())
            fs.data.name = os.path.splitext(fs.data.name)[-2] + f'_{random.randint(999,9999)}'+os.path.splitext(fs.data.name)[-1]
            fs.filename = fs.data.name
            fs.save()
            if fs.specific_user != '':
                specific_user_obj = User.objects.get(username=fs.specific_user)
                request_obj = Request(data_id=fs.id, data_owner=request.user.id, data_consumer=specific_user_obj.id, data_approve_status=True)
                request_obj.save()
                activity_obj = UserActivity(activity=f'{request.user.username} shared {fs.filename} to {specific_user_obj.username}.')
                activity_obj.save()
                notify.send(sender=User.objects.get(id=request.user.id), recipient=User.objects.get(id=specific_user_obj.id), verb='Got access to a file',description=f'{request.user.username} shared {fs.filename} with you')
            fs.specific_user = ''
            fs.save()
            encrypt_data(fs.data,base64_decode(fs.key))
            activity_obj = UserActivity(activity=f'{request.user.username} uploaded {fs.filename}.')
            activity_obj.save()
            messages.info(request, 'Successfully Uploaded !')
            return redirect('upload_data')
    else:
        form = DataForm()
    return render(request, 'upload_data.html', {'form': form,'date':date,'users':users},)

@login_required
def my_data(request):
    data_obj_list = []
    data_obj = Data.objects.all()
    for i in range(len(data_obj)):
        if request.user.id == data_obj[i].user_id:
            data_obj_list.append(data_obj[i])

    requests = Request.objects.filter(data_consumer=request.user.id)
    user_obj = User.objects.all()
    for request_ob in requests:
        for data in data_obj:
            if request_ob.data_id == data.id:
                request_ob.data_name = data.filename
                request_ob.data_path = data.data

    for request_ob in requests:
        for user in user_obj:
            if user.id == request_ob.data_owner:
                request_ob.data_owner_name = user.username + f"({user.email})"

    return render(request,"my_data.html",{'data':data_obj_list,'requests':requests})

@login_required
def delete_data(request, id):
    if request.user.is_superuser:
        data = Data.objects.get(id=id)
        data.data = str(data.data)+".enc"
        data.save()
        data.delete()
        return redirect("list_user_data")
    else:
        data = Data.objects.get(id=id)
        data.data = str(data.data)+".enc"
        data.save()
        data.delete()
        activity_obj = UserActivity(activity=f'{request.user.username} deleted {data.filename}.')
        activity_obj.save()
        return redirect("my_data")

@login_required
def download_data(request, path ,data):
    file_path = MEDIA_ROOT+'/'+ path +'/' + data
    data_obj = Data.objects.get(data=path +'/' + data)
    request_obj = Request.objects.all()
    download_approve = 0

    for request_ob in request_obj:
        if request_ob.data_id == data_obj.id:
            if request_ob.data_consumer == request.user.id:
                if request_ob.data_approve_status == 1:
                    download_approve = 1

    if request.user.is_superuser or request.user.id == data_obj.user_id or data_obj.universal == "Yes" or download_approve == 1:
        activity_obj = UserActivity(activity=f'{request.user.username} downloaded {data_obj.filename}.')
        activity_obj.save()
        subprocess.run(f'openssl enc -d -aes-256-cbc -in '+'"'+file_path+'.enc'+'"'+' -out '+'"'+file_path+'"'+' -k '+base64_decode(data_obj.key)+' -pbkdf2')
        file_wrapper = FileWrapper(open(file_path,'rb'))
        file_mimetype = mimetypes.guess_type(file_path)
        response = HttpResponse(file_wrapper, content_type=file_mimetype)
        response['X-Sendfile'] = file_path
        response['Content-Length'] = os.stat(file_path).st_size
        response['Content-Disposition'] = 'attachment; filename=%s' % smart_text(data)
        os.remove(file_path)
        return response
    return render(request,'403.html')

def generate_key():
    symbols = "@#$="
    characters = string.ascii_letters + string.digits + symbols
    password = ''.join(random.choice(characters) for i in range(32))
    return password

def base64_encode(string):
    string_bytes = string.encode("ascii")
    base64_bytes = base64.b64encode(string_bytes)
    base64_string = base64_bytes.decode("ascii")
    return base64_string

def base64_decode(base64_string):
    base64_bytes = base64_string.encode("ascii")
    string_bytes = base64.b64decode(base64_bytes)
    string = string_bytes.decode("ascii")
    return string

def encrypt_data(data,password):
    data = data.path
    subprocess.run(f'openssl enc -aes-256-cbc -in '+'"'+data+'"'+' -out '+'"'+data+'.enc'+'"'+' -k '+password+' -pbkdf2')
    os.remove(data)

@login_required
def list_data(request):
    data = Data.objects.all().exclude(user=request.user.id)
    users = User.objects.all().exclude(id=request.user.id)
    report_obj = ReportFlag.objects.all()
    data_filter = DataFilter(request.GET, queryset=data)
    data_requests = Request.objects.all().exclude(data_owner=request.user.id)
    for data in data_filter.qs:
        for data_request in data_requests:
            if data.id == data_request.data_id:
                if data_request.data_consumer == request.user.id:
                    if data_request.data_approve_status == 1:
                        data.button = 'download'
                    if data_request.data_approve_status == 0:
                        data.button = 'requested'

    for data in data_filter.qs:
        for i in report_obj:
            if data.id == i.data_id :
                if request.user.username in i.reported_by:
                    data.report_button = 'reported'
                else:
                    data.report_button = 'report'

    return render(request,"list_data.html",{'filter':data_filter.qs,'users':users})

@login_required
def manage_data_request(request):
    requests = Request.objects.filter(data_owner=request.user.id)
    data_obj = Data.objects.all()
    user_obj = User.objects.all()
    for request_ob in requests:
        for data in data_obj:
            if request_ob.data_id == data.id:
                request_ob.data_name = data.filename

    for request_ob in requests:
        for user in user_obj:
            if user.id == request_ob.data_consumer:
                request_ob.data_consumer_name = user.username + f"({user.email})"

    return render(request,"manage_data_request.html",{'requests':requests})

@login_required
def approve_data_request(request,id):
    request_ob = Request.objects.get(id=id)
    print(request_ob.id)
    request_ob.data_approve_status = True
    request_ob.save()
    data_obj = Data.objects.get(id=request_ob.data_id)
    user_obj = User.objects.get(id=request_ob.data_consumer)
    current_user_obj = User.objects.get(id=request.user.id)
    activity_obj = UserActivity(activity=f'{request.user.username} granted request to access {data_obj.filename} to {user_obj.username}.')
    activity_obj.save()
    notify.send(sender=current_user_obj, recipient=user_obj, verb='File Access Request Approved',description=f'{request.user.username} approved request to access {data_obj.filename}')
    return redirect('manage_data_request')

@login_required
def reject_data_request(request,id):
    request_ob = Request.objects.get(id=id)
    user_obj = User.objects.get(id=request_ob.data_consumer)
    current_user_obj = User.objects.get(id=request.user.id)
    data_obj = Data.objects.get(id=request_ob.data_id)
    activity_obj = UserActivity(activity=f'{request.user.username} rejected request to access {data_obj.filename} to {user_obj.username}.')
    activity_obj.save()
    notify.send(sender=current_user_obj, recipient=user_obj, verb='File Access Request Rejected',description=f'{request.user.username} rejected request to access {data_obj.filename}')
    request_ob.delete()
    return redirect('manage_data_request')

@login_required
def revoke_data_permission(request,id):
    request_ob = Request.objects.get(id=id)
    user_obj = User.objects.get(id=request_ob.data_consumer)
    current_user_obj = User.objects.get(id=request.user.id)
    data_obj = Data.objects.get(id=request_ob.data_id)
    activity_obj = UserActivity(activity=f'{request.user.username} revoked permission to access {data_obj.filename} from {user_obj.username}.')
    activity_obj.save()
    notify.send(sender=current_user_obj, recipient=user_obj, verb='File Access Permission Revoked',description=f'{request.user.username} revoked permission to access {data_obj.filename}')
    request_ob.delete()
    return redirect('manage_data_request')

@login_required
def request_data(request, id):
    data_obj = Data.objects.get(id=id)
    user_obj = User.objects.get(id=data_obj.user.id)
    current_user_obj = User.objects.get(id=request.user.id)
    request_obj = Request(data_id=data_obj.id, data_owner=data_obj.user_id, data_consumer=request.user.id)
    request_obj.save()
    activity_obj = UserActivity(activity=f'{request.user.username} requested access to {data_obj.filename} from {data_obj.user.username}.')
    activity_obj.save()
    notify.send(sender=current_user_obj, recipient=user_obj, verb='File Access Request',description=f'{request.user.username} requesting access to {data_obj.filename}')
    return redirect('list_data')

@superuser_only
def list_user_data(request):
    data = Data.objects.all()
    data_filter = DataFilter(request.GET, queryset=data)
    return render(request,"list_user_data.html",{'filter':data_filter.qs})

@superuser_only
def flagged_data(request):
    report_obj = ReportFlag.objects.all()
    return render(request,"flagged_data.html",{'report_obj':report_obj})

@login_required
def report_flag(request):
    report_obj = ReportFlag.objects.all()
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            data_obj = Data.objects.get(id=report.data_id)
            for i in report_obj:
                if data_obj.id == i.data_id:
                    report_obj_new = ReportFlag.objects.get(data_id=data_obj.id)
                    report_obj_new.report_count = report_obj_new.report_count + 1
                    report_obj_new.reported_by = f'{report_obj_new.reported_by} <br>{request.user.username}'
                    report_obj_new.report_comment = f'{report_obj_new.report_comment} <br>{request.user.username}: {report.report_comment}'
                    report_obj_new.save()
                    activity_obj = UserActivity(activity=f'{request.user.username} reported {data_obj.filename} as inappropriate.')
                    activity_obj.save()
                    notify.send(sender=User.objects.get(id=request.user.id), recipient=User.objects.get(id=1), verb='Review File',description=f'{request.user.username} reported {data_obj.filename} as inappropriate')
                    return redirect('list_data')
            report.report_count = 1
            report.reported_by = request.user.username
            report.report_comment = f'{request.user.username}: {report.report_comment}'
            report.save()
            activity_obj = UserActivity(activity=f'{request.user.username} reported {data_obj.filename} as inappropriate.')
            activity_obj.save()
            notify.send(sender=User.objects.get(id=request.user.id), recipient=User.objects.get(id=1), verb='Review File',description=f'{request.user.username} reported {data_obj.filename} as inappropriate')
            return redirect('list_data')
    else:
        form = ReportForm()
    return redirect('list_data')

@superuser_only
def remove_flag(request, id):
    report_obj = ReportFlag.objects.get(id=id)
    report_obj.delete()
    return redirect('flagged_data')

@superuser_only
def delete_inappropriate(request, id):
    data = Data.objects.get(id=id)
    data.data = str(data.data)+".enc"
    data.save()
    data.delete()
    return redirect("flagged_data")

@superuser_only
def clear_logs(request):
    activity_obj = UserActivity.objects.all()
    activity_obj.delete()
    return redirect("home")

@superuser_only
def list_user_activity(request):
    activity = UserActivity.objects.all()
    activity_filter = UserActivityFilter(request.GET, queryset=activity)
    return render(request,"list_user_activity.html",{'filter':activity_filter.qs})

def about(request):
    return render(request, 'about.html')

def file_expiration_check():
    while True:
        time.sleep(1)
        data = Data.objects.all()
        for i in data:
            if i.expires_on < timezone.now():
                print(f'{i.filename} expired !!')
                i.data = str(i.data)+".enc"
                i.save()
                i.delete()

def file_expiration_check_process():
    process=threading.Thread(target=file_expiration_check)
    process.daemon = True
    process.start()

file_expiration_check_process()
