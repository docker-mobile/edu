from django.db import models
from django.utils import timezone

# Create your models here.
class Post(models.Model):
    header_img = models.ImageField(upload_to='static/assets/blog/image')
    category = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=230)
    content = models.TextField(max_length=7000)
    date = models.DateField(default=timezone.now())
    file = models.FileField(upload_to='static/assets/blog/file', default=None, null=True)
    view = models.IntegerField(default=0)