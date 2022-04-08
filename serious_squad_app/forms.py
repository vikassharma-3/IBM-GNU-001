from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from .models import *

def validate_email(value):
    if User.objects.filter(email = value).exists():
        raise ValidationError((f"{value} already exists !!!."),params = {'value':value})

def validate_user(value):
    if not User.objects.filter(username = value).exists():
        raise ValidationError((f"Can't share file with '{value}'. User '{value}' does not exist !!!."),params = {'value':value})

def validate_file_size(value):
    filesize= value.size
    
    if filesize > 15728640:
        raise ValidationError("The maximum file size that can be uploaded is 15MB")
    else:
        return value

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, required=True, validators = [validate_email])

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )

class DataForm(forms.ModelForm):
    specific_user = forms.CharField(validators = [validate_user], required = False)
    data = forms.FileField(validators = [validate_file_size, FileExtensionValidator( ['doc','pdf','txt','odt','rtf','wpd','ods','xls','xlsm','xlsx','pptx','ppt','pps','odp','key','csv','dat','db','dbf','log','sql','tmp','bak','tar','bin','7z','rar','tar.gz','bz','zip','mp3','mpa','ogg','wav','wma','vcf','pst','ost','bmp','gif','ico','jpeg','png','psd'] )])
    class Meta:
        model = Data
        fields = ('title','data','description','expires_on','universal','specific_user',)