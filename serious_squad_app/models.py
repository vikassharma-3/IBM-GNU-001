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
    key = models.CharField(max_length=255, blank=True)

    def delete(self, *args, **kwargs):
        self.data.delete()
        super().delete(*args, **kwargs)
        