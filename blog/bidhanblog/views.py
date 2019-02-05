from django.shortcuts import render, get_object_or_404, redirect, Http404
from django.urls import reverse, reverse_lazy
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
import itertools

""" django views """
from django.views.generic.edit import View, DeleteView, FormMixin
from django.views.generic import ListView, DetailView

""" contrib and message """
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

""" utils """
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string

""" models """
from bidhanblog.models import Category, Tags, Post, Comment, User

""" forms """
from bidhanblog.forms import LoginForm, SignupForm, PostForm, PostEditForm, CommentForm, CommentEditForm, CommentReplyForm
from bidhanblog.forms import UpdateEmailForm, UserSettinngsForm
from django.contrib.auth.forms import PasswordResetForm, PasswordResetForm, PasswordChangeForm

""" tokens """
from bidhanblog.tokens import AccountActivationTokenGenerator, account_activation_token

# Authentication View
# Signup View

class SignupView(View):
    form_class = SignupForm
    template_name = 'auth/signup.html'

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form':form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data['password']
            user.set_password(password)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Activate Your Account'
            message = render_to_string('auth/account_activation_email.html',{
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            return redirect('bidhanblog:account_activation_sent')
            
        else:
            return render(request, self.template_name, {'form':form})

def account_activation_sent(request):
    return render(request, 'auth/account_activation_sent.html')

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, ObjectDoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.email_confirmed = True
        user.save()
        login(request, user)
        return redirect('bidhanblog:home')
    else:
        return render(request, 'auth/account_activation_invalid.html')

# Authentication 
# Login View

class LoginView(View):
    template_name = 'auth/login.html'
    form_class = LoginForm

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form':form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('bidhanblog:home')
                else:
                    messages.error(request, 'User is not active')
                    return redirect('bidhanblog:signup')
            else:
                messages.error(request, 'Username or Password is not correct')
                return redirect('bidhanblog:login')
        
        else:
            return render(request, self.template_name, {'form':form})

# Logout View

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('bidhanblog:home')

# Starting Page
# Home page will be shown to login User
# Home page along with Login sidenav will be shown to Anonymous User
#
# Home View

class HomeView(FormMixin, ListView):
    template_name = 'bidhanblog/home.html'
    model = Post
    form_class = LoginForm
    context_object_name = 'all_posts'

    def get_queryset(self):
        return Post.objects.order_by('-date')

    def get_context_data(self):
        context = super(HomeView, self).get_context_data()
        context['all_categories'] = Category.objects.all().order_by('name')
        context['login_form'] = LoginForm()
        return context

    def get_success_url(self):
        return reverse('bidhanblog:home')

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('bidhanblog:home')
                else:
                    messages.error(request, 'Username or Password is invalid!')
                    return redirect('bidhanblog:login')
            else:
                messages.error(request, 'Username or Password is invalid!')
                return redirect('bidhanblog:home')
        else:
            return render(request, self.template_name, {'form':form})

# post detail page to show post detail, comment and comment reply
# open with /slug
#
# Post Detail View

class PostDetailView(DetailView):
    model = Post
    template_name = 'bidhanblog/detail.html'

    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        context['commentform'] = CommentForm()
        context['commentreplyform'] = CommentReplyForm()
        context['all_post_comment'] = Comment.objects.filter(post__slug=self.kwargs['slug'], parent=None).order_by('date')
        return context

    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        form = CommentForm(request.POST)
        replyform = CommentReplyForm(request.POST)

        if form.is_valid():
            obj  = form.save(commit=False)
            obj.post = post
            obj.author = self.request.user
            obj.save()
            return redirect('bidhanblog:detail', post.slug)

        if replyform.is_valid():
            parent_obj = None
            try:
                parent_id = int(request.POST.get('parent_id'))
            except:
                parent_id = None

            if parent_id:
                parent_obj = Comment.objects.get(id=parent_id)
                obj = replyform.save(commit=False)
                obj.parent = parent_obj
                obj.post = get_object_or_404(Post, slug=slug)
                obj.author = self.request.user
                obj.save()
                return redirect('bidhanblog:detail', post.slug)

# create post with category and tags
# Post create view

class PostCreateView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'login'
    form_class = PostForm
    template_name = 'bidhanblog/createpost.html'

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form':form})

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.author = self.request.user
            obj.save()
            return redirect('bidhanblog:detail', obj.slug)
        else:
            return render(request, self.template_name, {'form':form})

# Edit your post only by the creator
# post edit view

class PostEditView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'login'
    form_class = PostEditForm
    template_name = 'bidhanblog/editpost.html'
    
    def get(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        if not post.author == self.request.user:
            raise PermissionDenied('This is not available to you!')
        else:
            form = self.form_class(instance=post)
        return render(request, self.template_name, {'form':form})

    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        form = self.form_class(request.POST,request.FILES, instance=post)

        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return redirect('bidhanblog:detail', post.slug)

        else:
            return render(request, self.template_name, {'form':form})

# Edit the comment
# comment edit view

class CommentEditView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'login'
    form_class = CommentEditForm
    template_name = 'bidhanblog/editcomment.html'
    
    def get(self, request, slug, pk):
        comment = get_object_or_404(Comment, pk=pk)
        if not comment.author == self.request.user:
            raise PermissionDenied('This is not available to you!')
        else:
            form = self.form_class(instance=comment)
        return render(request, self.template_name, {'form':form})

    def post(self, request, slug, pk):
        post = get_object_or_404(Post, slug=slug)
        comment = get_object_or_404(Comment, pk=pk)
        form = self.form_class(request.POST, instance=comment)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            return redirect('bidhanblog:detail', post.slug)

        else:
            return render(request, self.template_name, {'form':form})

# delete post only by creator
# Post Delete View

class PostDeleteView(LoginRequiredMixin, DeleteView):
    login_url = '/login/'
    redirect_field_name = 'login'
    model = Post
    success_url = reverse_lazy('bidhanblog:home')

    def get_object(self, queryset=None):
        obj = super(PostDeleteView, self).get_object()
        if not obj.author == self.request.user:
            raise PermissionDenied("You don't have the permission")
        return obj

# Delete Comment only by creator
# Comment Delete View

class CommentDeleteView(LoginRequiredMixin, DeleteView):
    login_url = '/login/'
    redirect_field_name = 'login'
    model = Comment

    def get_success_url(self):
        post = self.object.post
        return reverse_lazy('bidhanblog:detail', kwargs={'slug' : post.slug})

    def get_object(self, queryset=None):
        obj = super(CommentDeleteView, self).get_object()
        if not obj.author == self.request.user:
            raise PermissionDenied("You don't have the permission")
        return obj    

# Show all posts of a category
# Category Detail View

class CategoryContent(DetailView):
    model = Category
    template_name = 'mechinpy/categorycontent.html'
    slug_field = 'name'
    slug_url_kwarg = 'name'

# Show all posts of a single tags
# Tag Detail View

class TagsContent(DetailView):
    model = Tags
    template_name = 'bidhanblog/tagscontent.html'
    slug_field = 'name'
    slug_url_kwarg = 'name'

# Search User and Post
# Search View

class SearchView(ListView):
    model = Post
    template_name = 'bidhanblog/search.html'
    context_object_name = 'all_search_results'
    def get_queryset(self):
        result = super(SearchView, self).get_queryset()
        query = self.request.GET.get('q')
        if query:
            postresult = Post.objects.filter(title__contains=query)
            userresult = User.objects.filter(username__contains=query)
            tagsresult = Tags.objects.filter(name__contains=query)
            result = itertools.chain(postresult, userresult, tagsresult)
        else:
            result = None
        return result


# User Section
# User Profile 

class UserProfileView(LoginRequiredMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'login'
    template_name = 'bidhanblog/userprofile.html'
    context_object_name = 'user_content'
    allow_empty = False

    def get_queryset(self):
        return User.objects.filter(username=self.kwargs['username'])

    def get_context_data(self):
        context = super(UserProfileView, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['user_about'] = User.objects.filter(username=self.kwargs['username'])
        context['user_post'] = Post.objects.filter(author__username=self.kwargs['username']).order_by('-date')
        return context

# Settings

class UserSettingsView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'login'
    template_name = 'bidhanblog/profilesetting.html'
    model = User
    allow_empty = False
    context_object_name = 'thisuser'
    form_class = UserSettinngsForm

    def get(self, request, username):
        user = get_object_or_404(User, username=self.kwargs['username'])
        if not self.request.user == user:
            raise Http404
        else:
            form = self.form_class(instance=user)
        return render(request, self.template_name, {'form':form})

    def post(self, request, username):
        user = get_object_or_404(User, username=self.kwargs['username'])
        if not self.request.user == user:
            raise Http404
        else:
            form = self.form_class(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            return redirect('bidhanblog:userprofile', user.username)
        else:
            render(request, self.template_name, {'form':form})

# User Email change
class ChangeEmail(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'login'
    template_name = 'privacy/update_email.html'
    model = User
    allow_empty = False
    context_object_name = 'thisuser'
    form_class = UpdateEmailForm

    def get(self, request, username):
        user = get_object_or_404(User, username=self.kwargs['username'])
        if not self.request.user == user:
            raise Http404
        else:
            form = self.form_class(instance=user)
        return render(request, self.template_name, {'form':form})

    def post(self, request, username):
        user = get_object_or_404(User, username=self.kwargs['username'])
        if not self.request.user == user:
            raise Http404
        else:
            form = self.form_class(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.email_confirmed = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Update Your Email Address'
            message = render_to_string('privacy/email.html',{
                'user':user,
                'domain': current_site.domain,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            return redirect('bidhanblog:update_email_sent')
        else:
            return render(request, self.template_name, {'form':form})

def update_email_sent(request):
    return render(request, 'privacy/update_email_sent.html')

def UpdateEmail(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, ObjectDoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.email_confirmed = True
        user.save()
        messages.success(request, 'Your email address successfully updated')
        return redirect('bidhanblog:userprofile', user.username)
    else:
        return render(request, 'privacy/update_email_invalid.html')

# User Password Change

@login_required(login_url='/login/')
def ChangePassword(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Your password was successfully updated! You can go to your profile')
            return redirect('bidhanblog:change_password')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/password_change.html', {
        'form': form
    })