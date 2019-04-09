from django.db import models
from django.contrib.auth.models import User


class Room(models.Model):
    name = models.CharField(max_length=128)
    protected = models.BooleanField(default=False)
    password = models.CharField(max_length=64, null=True, blank=True)

    admin = models.ForeignKey(User, related_name="owned_rooms", on_delete=models.DO_NOTHING)
    moderators = models.ManyToManyField(User, related_name="moderated_rooms", null=True, blank=True)
    members = models.ManyToManyField(User, related_name="rooms", null=True, blank=True)

    def __str__(self):
        return f"Room(name: {self.name}, owner: {self.admin.username})"


class Message(models.Model):
    author = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="messages")
    content = models.TextField(max_length=1024)
    posted_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-id', )

    def __str__(self):
        return f"Message (author: {self.author.username}, posted at: {str(self.posted_at)})"
