from django.db import models
from notifications.base.models import AbstractNotification
# Create your models here.

class Notification(AbstractNotification):

    class Meta(AbstractNotification.Meta):
        abstract = False
        app_label = 'serious_squad_app'
