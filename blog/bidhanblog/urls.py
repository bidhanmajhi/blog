from django.urls import path
from bidhanblog import views

app_name = 'bidhanblog'
urlpatterns = [
    #SignUp
    path('signup/', views.SignupView.as_view(), name='signup'),

    path('account-activation-sent/', views.account_activation_sent, name='account_activation_sent'),

    path('activate/<uidb64>/<token>/', views.activate, name='activate'),

    # Authentication - Login Logout
    path('login/', views.LoginView.as_view(), name='login'),
    
    path('logout/', views.LogoutView.as_view(), name='logout'),

    #search field
    path('search/', views.SearchView.as_view(), name='search'),

    # Home Page
    # 
    path('', views.HomeView.as_view(), name='home'),

    # Post
    # Create Post
    path('create/', views.PostCreateView.as_view(), name='createpost'),

    # Detail Post
    path('post/<slug:slug>/', views.PostDetailView.as_view(), name='detail'),

    # Edit Post
    path('post/<slug:slug>/edit/', views.PostEditView.as_view(), name='editpost'),

    # Delete Post
    path('post/<slug:slug>/delete/', views.PostDeleteView.as_view(), name='deletepost'),

    # Comment
    # Edit Comment
    path('post/<slug:slug>/comment/<int:pk>/edit/', views.CommentEditView.as_view(), name='editcomment'),

    # Delete Comment
    path('post/<slug:slug>/comment/<int:pk>/delete/', views.CommentDeleteView.as_view(), name='deletecomment'),

    # category content
    path('category/<slug:name>/', views.CategoryContent.as_view(), name='categorycontent'),

    # User
    # User Detail
    path('user/<str:username>/', views.UserProfileView.as_view(), name='userprofile'),

    # User Setting
    path('user/<str:username>/settings/', views.UserSettingsView.as_view(), name='usersettings'),

    # Email Update
    path('user/<str:username>/privacy/update/email/', views.ChangeEmail.as_view(), name='change_email'),

    path('user/privacy/update/email/sent/', views.update_email_sent, name='update_email_sent'),

    path('user/privacy/update/email/<uidb64>/<token>/', views.UpdateEmail, name='update-email'),

    # Password Change
    path('user/privacy/update/password/', views.ChangePassword , name='change_password'),

]