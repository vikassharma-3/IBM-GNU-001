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

# Create your views here.
def home(request):
    title = ""
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return render(request, 'admin_dashboard.html')
        if request.user.is_superuser is False:
            return render(request, 'data_owner_dashboard.html')
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
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


# def user_login(request):
#     username = password = ''
#     print('test1')
#
#     if request.POST:
#
#         username = request.POST['username']
#         password = request.POST['password']
#         print('test2')
#
#         user = authenticate(username=username, password=password)
#         if user is not None:
#             print('test3')
#             if user.is_active:
#                 login(request, user)
#                 return HttpResponseRedirect('home')
#     return render(request, 'user_login.html', {'form': form})

# def user_login(request):
#     if request.method == "POST":
#         form = AuthenticationForm(request, data=request.POST)
#         if form.is_valid():
#             username = form.cleaned_data.get('username')
#             password = form.cleaned_data.get('password')
#             user = authenticate(username=username, password=password)
#             if user is not None:
#                 print('not none')
#                 if user.is_active:
#                     print('is active')
#                     login(request, user)
#                     messages.info(request, f'You are now logged in as {username}.')
#                     return redirect('home')
#     form = AuthenticationForm()
#     return render(request, 'user_login.html', {'form': form})

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

def data_owner_dashboard(request):
    if request.user.is_authenticated:
        return render(request, 'data_owner_dashboard.html')
    else:
        return redirect('login')

def admin_dashboard(request):
    if request.user.is_authenticated:
        return render(request, 'admin_dashboard.html')
    else:
        return redirect('login')

def user_list(request):
    users = User.objects.all()
    return render(request,"user_list.html",{'users':users})

def approve_user(request, id):
    user = User.objects.get(id=id)
    user.is_active = 1
    user.save()
    return redirect("user_list")
