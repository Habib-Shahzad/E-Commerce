from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.CharField(max_length=64)
    category = models.CharField(max_length=64)
    description = models.CharField(max_length=164)
    image = models.CharField(max_length=900)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.FloatField()
    running = models.BooleanField(default=True)
    
class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    bid = models.FloatField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.CharField(max_length=164)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, default="")

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, null=True)

