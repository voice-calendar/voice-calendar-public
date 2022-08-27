from django.db import models
from django.contrib.auth.models import User

class Calendar(models.Model):
  name = models.CharField(max_length=100, unique=True)
  creator = models.ForeignKey(User, null=True, related_name='calendars',
    on_delete=models.CASCADE
  )

  def __str__(self):
    return self.name

class Event(models.Model):
  title = models.CharField(max_length=100)
  date = models.DateField(auto_now_add=True)
  time = models.TimeField(auto_now_add=True)
  location = models.CharField(max_length=400)
  description = models.CharField(max_length=4000)
  isBusy = models.BooleanField()
  calendar = models.ForeignKey(Calendar, related_name='events',
    on_delete=models.CASCADE
  )
  creator = models.ForeignKey(User, related_name='events',
     on_delete=models.CASCADE
  )
