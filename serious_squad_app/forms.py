from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import *

def validate_email(value):
    if User.objects.filter(email = value).exists():
        raise ValidationError((f"{value} already exists !!!."),params = {'value':value})

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, required=True, validators = [validate_email])

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )

class DataForm(forms.ModelForm):
    class Meta:
        model = Data
        fields = ('title','data','description','expires_on')