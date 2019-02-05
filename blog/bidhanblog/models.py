from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import os
from uuid import uuid4
from django.utils.deconstruct import deconstructible
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.core.mail import send_mail

""" Change the uploaded image name and format """
@deconstructible
class PathAndRename(object):
    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = "png"
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)
        # return the whole path to the file
        return os.path.join(self.path, filename)

""" User Manager """
class UserManager(BaseUserManager):
    def create_user(self, username, email, password):
        if not email:
            return ValueError('Add Your Email')
        if not username:
            return ValueError('Add Your Unique Username')
        if not password:
            return ValueError('Add Your Password')

        user = self.model(
            email = self.normalize_email(email),
            username = username
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password):
        user = self.create_user(username, email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=40, unique = True)
    email = models.EmailField(unique=True)

    firstname = models.CharField(max_length=50, blank=True, null=True)
    lastname = models.CharField(max_length=50, blank=True, null=True)

    """ profile requirement optional """
    avatar = models.ImageField(upload_to=PathAndRename('image/avatar/'), blank=True, null=True)
    about = models.CharField(blank=True, null=True, max_length=140)
    phone = models.CharField(blank=True, null=True, max_length=10)
    birth = models.DateField(auto_now=False, blank=True, null=True)

    """ date joined """
    date_joined = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    """ Boolean Fields """
    email_confirmed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_creator = models.BooleanField(default=False)
    phone_confirmed = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    def get_full_name(self):
        if self.firstname and self.lastname:
            return self.firstname + ' ' + self.lastname
        elif self.firstname and not self.lastname:
            return self.firstname
        elif self.lastname and not self.firstname:
            return self.lastname
        else:
            return self.username

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    """ def profileavatar(self):
        if self.avatar:
            return self.avatar
        else:
            return '/media/image/avatar/default.png'  """

""" Category And Tags """
class Category(models.Model):
    name = models.CharField(max_length = 24)
    detail = models.TextField(blank=True, null=True)
    thumbnail = models.ImageField(upload_to=PathAndRename('images/thumbnail/category/'), blank=True, null=True)

    objects = models.Manager()

    def __str__(self):
        return self.name

# These are the tags that will be attached to posts

class Tags(models.Model):
    name = models.CharField( max_length = 24 )
    detail = models.TextField(blank=True, null=True)
    
    objects = models.Manager()

    def __str__(self):
        return self.name

# The Post model, it contains 
# title, text, image, 
# foreign key refernce with User, Category, Tag

class Post(models.Model):
    title = models.CharField(max_length = 100)
    slug = models.SlugField(max_length=100, blank=True, null=True)
    text = models.TextField()
    image = models.ImageField(upload_to=PathAndRename('images/post/'), blank=True, null=True)
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='postcategory')
    tags = models.ManyToManyField(Tags, related_name='posttags', blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    editdate = models.DateTimeField(auto_now=True,blank=True, null=True)

    is_flagged = models.BooleanField(default=False)
    is_duplicate = models.BooleanField(default=False)

    objects = models.Manager()

    def save(self):
        self.slug = slugify(self.title) + '-' + str(self.pk)
        super(Post, self).save()

    def __str__(self):
        return self.title


# The comment section of post, 
# self referencing model, for comment reply

class Comment(models.Model):
    text = models.TextField(blank=True, null=True)
    chartext = models.CharField(blank=True, null=True, max_length = 280)
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    
    date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    editdate = models.DateTimeField(auto_now=True, blank=True, null=True)
    is_flagged = models.BooleanField(default=False)
    is_duplicate = models.BooleanField(default=False)

    objects = models.Manager()

    def __str__(self):
        if self.text:
            return '[Comment] : ' + self.text
        else:
            return '[Comment Reply] : ' + self.chartext