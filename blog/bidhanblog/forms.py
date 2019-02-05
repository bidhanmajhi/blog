from django import forms
from django.template.defaultfilters import slugify
from django.core.validators import validate_email

# Models from Mechinpy
from bidhanblog.models import User, Post, Comment, Category, Tags

# Validation Error check
from django.core.exceptions import ValidationError

# Authentication User
# SignUp Form with mandatory email, username and password
# Signup form

class SignupForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'class-signup', 'placeholder':'Enter an unique Username'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class':'class-signup', 'placeholder':'Enter Firstname'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class':'class-signup', 'placeholder':'Enter Lastname'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'class-signup', 'placeholder':'Enter your Email'}))
    password = forms.CharField(min_length=8, widget=forms.PasswordInput(attrs={'class':'class-signup', 'placeholder':'Enter a password with minimum 8 characters'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'class-signup', 'placeholder':'Confirm Your password'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name','username', 'email', 'password', 'password2']

    def clean(self):
        cleaned_data = super(SignupForm, self).clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')

        if password != password2:
            raise forms.ValidationError('Passwords do not match!')
    
    def clean_email(self):
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')
        
        if email and User.objects.filter(email=email).exclude(username=username).exists():
            raise forms.ValidationError('This email is already in use! Try another email.')
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')
        
        if username and User.objects.filter(username__iexact=username).exclude(email=email).exists():
            raise forms.ValidationError('This username has already been taken!')
        return username

# Authenticate User with
# Username And Password
# Login Form
class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'class-login', 'placeholder':'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'class-login', 'placeholder':'Password'}))
    
    class Meta:
        model = User
        fields = ['username', 'password']

# Password Reset Form
# Build In Password Reset Form

# Post Form 
class PostForm(forms.ModelForm):
    title =  forms.CharField(widget = forms.TextInput(attrs={'class':'title', 'placeholder':'Add title', 'maxlength':'100'}))
    category = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label="Select Category")
    tags = forms.ModelMultipleChoiceField(required = False, queryset=Tags.objects.all())
    image = forms.ImageField(required=False, widget = forms.FileInput(attrs={'class':'image'}))
    text = forms.CharField(widget = forms.Textarea(attrs={'class':'text', 'placeholder':'Describe with minimum 30 letters', 'minlength':'30'}))

    class Meta:
        model = Post
        fields = ['title', 'category', 'text', 'tags' , 'image']

    # def clean_title(self):
    #     title = self.cleaned_data.get('title')
    #     slug = slugify(title)

    #     if Post.objects.filter(slug=slug).exists():
    #         raise ValidationError('This title already exists, either change the title or add something else')
    #     return title

# Comment Form 
# 
class CommentForm(forms.ModelForm):
    text = forms.CharField(widget = forms.Textarea(attrs={'class':'commenttext', 'placeholder':'Add your comment/answer here with minimum 20 characters', 'minlength':'20'}))

    class Meta:
        model = Comment
        fields = ['text']

# Comment Reply Form
class CommentReplyForm(forms.ModelForm):
    chartext = forms.CharField(widget = forms.TextInput(attrs={'class':'chartext', 'placeholder':'Reply to this comment', 'minlength':'5', 'maxlength':'240'}))

    class Meta:
        model = Comment
        fields = ['chartext']

#
# Edit Form 
# Post Edit Form
class PostEditForm(forms.ModelForm):
    text = forms.CharField(widget = forms.Textarea(attrs={'class':'edittext', 'placeholder':'Describe with minimum 30 letters', 'minlength':'30'}))
    image = forms.ImageField(required=False, widget = forms.FileInput(attrs={'class':'editimage'}))
    
    class Meta:
        model = Post
        fields = ['text', 'image']

# Comment Edit Form
class CommentEditForm(forms.ModelForm):
    text = forms.CharField(widget = forms.Textarea(attrs={'class':'editcommenttext', 'placeholder':'Add your comment/answer here with minimum 20 characters', 'minlength':'20'}))

    class Meta:
        model = Comment
        fields = ['text']


# User Settings
# User Settings Form
class UserSettinngsForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['firstname', 'lastname', 'about']

# Update Email Form
class UpdateEmailForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'update-email', 'placeholder':'example@gmail.com'}))
    class Meta:
        model = User
        fields = ['email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already in use! Try another email.')
        return email