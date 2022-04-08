from django.db import models
from notifications.base.models import AbstractNotification
from django.contrib.auth.models import User

class Notification(AbstractNotification):
    class Meta(AbstractNotification.Meta):
        abstract = False
        app_label = 'serious_squad_app'

def user_directory_path(instance, filename):
    return '{0}/{1}'.format(instance.user.username, filename)

class Data(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=False, default='')
    filename = models.CharField(max_length=255, blank=True)
    data = models.FileField(upload_to=user_directory_path)
    description = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    expires_on = models.DateTimeField(null=True)
    key = models.CharField(max_length=255, blank=True)
    inappropiate_flag = models.BooleanField(blank = False, default=False)
    universal = models.CharField(max_length=255, blank=False, default='No')
    specific_user = models.CharField(max_length=255,null=True)

    def delete(self, *args, **kwargs):
        self.data.delete()
        super().delete(*args, **kwargs)

class Request(models.Model):
    data = models.ForeignKey(Data, on_delete=models.CASCADE)
    data_owner = models.IntegerField(blank=False)
    data_consumer = models.IntegerField(blank=False)
    data_approve_status = models.BooleanField(blank=False, default=False)
    requested_at = models.DateTimeField(auto_now_add=True)
