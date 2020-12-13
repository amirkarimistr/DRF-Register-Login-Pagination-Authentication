from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


def validate_file_extension(value):
    import os
    from django.core.exceptions import ValidationError

    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.jpg', '.png']
    if not ext.lower() in valid_extensions:
        raise ValidationError(" Format not supported ! ")


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.FileField(upload_to='files/user_avatar', blank=False, validators=[validate_file_extension])
    description = models.CharField(max_length=512, null=False, blank=False)

    def __str__(self):
        return self.user.username


class Article(models.Model):
    title = models.CharField(max_length=128, null=False, blank=False)
    cover = models.ImageField(default='files/default.jpg', upload_to='files/article_cover')
    content = models.TextField(null=False, blank=False)
    created_at = models.DateTimeField(default=timezone.now)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    promote = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('index')


class Category(models.Model):
    title = models.CharField(max_length=128, null=False, blank=False)
    cover = models.FileField(upload_to='files/category_cover', null=False, blank=False, validators=[validate_file_extension])

    def __str__(self):
        return self.title


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)