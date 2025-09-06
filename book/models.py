from django.db import models

from .consts import MAX_RATE
from cloudinary.models import CloudinaryField 

RATE_CHOICES = [(x, str(x)) for x in range(0, MAX_RATE + 1)]

CATEGORY=(('business', 'ビジネス'), ('life', '生活'), ('sensitve', 'エロ'), ('other', 'その他'))
class Book(models.Model):
    title=models.CharField(max_length=100)
    text=models.TextField()
    thumbnail=CloudinaryField('image', null=True, blank=True)
    category=models.CharField(
        max_length=100,
        choices=CATEGORY
    )
    user=models.ForeignKey('auth.User', on_delete=models.CASCADE)
    
    def __str__(self):
        return self.title

class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    text = models.TextField()
    rate = models.IntegerField(choices=RATE_CHOICES)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def __str__(self):
        return self.title
# Create your models here.