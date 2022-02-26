from django.shortcuts import render, redirect
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
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {
        'form': form
    })

def user_logout(request):
    logout(request)
    return redirect('home')

def user_dashboard(request):
    if request.user.is_authenticated:
        return render(request, 'user_dashboard.html')
    else:
        return redirect('login')

def admin_dashboard(request):
    if request.user.is_authenticated:
        return render(request, 'admin_dashboard.html')
    else:
        return redirect('login')

def manage_user(request):
    users = User.objects.all()
    return render(request,"manage_user.html",{'users':users})

def approve_user(request, id):
    user = User.objects.get(id=id)
    user.is_active = 1
    user.save()
    return redirect("manage_user")

def deactivate_user(request, id):
    user = User.objects.get(id=id)
    user.is_active = 0
    user.save()
    return redirect("manage_user")

def delete_user(request, id):
    user = User.objects.get(id=id)
    user.delete()
    try:
        notification = Notification.objects.get(actor_object_id=id)
        notification.delete()
    except:
        pass
    return redirect("manage_user")

def clear_notification(request):
    notification = Notification.objects.all()
    notification.delete()
    return redirect('home')
