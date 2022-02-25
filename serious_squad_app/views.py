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
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            user_obj = User.objects.all()
            for i in range(len(user_obj)):
                if username == user_obj[i].username:
                    user_obj[i].is_active = 0
                    user_obj[i].save()
                    n_recipient = User.objects.get(id=user_obj[0].id)
                    n_sender = User.objects.get(id=user_obj[i].id)
                    n_message = "Test"
                    notify.send(sender=n_sender, recipient=n_recipient, verb='Notification',description=n_message)
                    e_subject = f'Pending Approval'
                    e_message = f'Hi admin,\n\nUser {user_obj[i].username} is requesting for approval'
                    e_recepient = 'serioussquad.ibads@gmail.com'
                    send_mail(e_subject,e_message, EMAIL_HOST_USER, [e_recepient], fail_silently = True)
            messages.success(request, f'Successfully created account for {username} and will be accessable after administrator approval !!!')
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
            update_session_auth_hash(request, user)  # Important!
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
    users = User.objects.all()
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
    try:
        notification = Notification.objects.get(actor_object_id=id)
        notification.delete()
    except:
        pass
    return redirect("manage_user")

@superuser_only
def clear_notification(request):
    notification = Notification.objects.all()
    notification.delete()
    return redirect('home')

def upload_data(request):
    if request.method == 'POST':
        form = DataForm(request.POST, request.FILES,)
        if form.is_valid():
            fs=form.save(commit=False)
            fs.user_id = request.user.id
            fs.key = generate_key()
            fs.filename = fs.data.name
            fs.save()
            encrypt_data(fs.data,fs.key)
            messages.info(request, 'Successfully Uploaded !')
            return redirect('upload_data')
    else:
        form = DataForm()
    return render(request, 'upload_data.html', {'form': form})

def my_data(request):
    data_obj_list = []
    data_obj = Data.objects.all()
    for i in range(len(data_obj)):
        if request.user.id == data_obj[i].user_id:
            data_obj_list.append(data_obj[i])
    return render(request,"my_data.html",{'data':data_obj_list})

def delete_data(request, id):
    data = Data.objects.get(id=id)
    data.data = str(data.data)+".enc"
    data.save()
    data.delete()
    return redirect("my_data")

def download_data(request, path ,data):
    file_path = MEDIA_ROOT+'/'+ path +'/' + data
    data_obj = Data.objects.get(data=path +'/' + data)
    subprocess.run(f'openssl enc -d -aes-256-cbc -in '+'"'+file_path+'.enc'+'"'+' -out '+'"'+file_path+'"'+' -k '+data_obj.key+' -pbkdf2')
    file_wrapper = FileWrapper(open(file_path,'rb'))
    file_mimetype = mimetypes.guess_type(file_path)
    response = HttpResponse(file_wrapper, content_type=file_mimetype )
    response['X-Sendfile'] = file_path
    response['Content-Length'] = os.stat(file_path).st_size
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_text(data)
    os.remove(file_path)
    return response

def generate_key():
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for i in range(8))
    return password

def encrypt_data(data,password):
    data = data.path
    subprocess.run(f'openssl enc -aes-256-cbc -in '+'"'+data+'"'+' -out '+'"'+data+'.enc'+'"'+' -k '+password+' -pbkdf2')
    os.remove(data)