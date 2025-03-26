from django.urls import path, reverse
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('blog/', views.home, name='home_blog'),
    path('blog/blogs/', views.blog_list, name='blog_list'),
    path('blog/bloggers/', views.blogger_list, name='blogger_list'),
    path('blog/blogger/<int:user_id>/', views.blogger_detail, name='blogger_detail'),
    path('blog/create/', views.create_blog_post, name='create_blog_post'),
    path('blog/edit/<slug:slug>/', views.edit_blog_post, name='edit_blog_post'),
    path('blog/delete/<slug:slug>/', views.delete_blog_post, name='delete_blog_post'),
    path('blog/post/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('login/', views.custom_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('register/', views.register, name='register'),
    path('blog/<slug:slug>/comment/', views.create_comment, name='create_comment'),
    path('blog/<slug:slug>/like/', views.like_post, name='like_post'),
    path('blog/comment/<int:comment_id>/like/', views.like_comment, name='like_comment'),
    path('blog/<slug:slug>/share/', views.share_post, name='share_post'),
    path('blog/user/<str:username>/follow/', views.follow_user, name='follow_user'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('blog/user/<int:user_id>/followers/', views.followers_list, name='followers_list'),
    path('blog/user/<int:user_id>/following/', views.following_list, name='following_list'),
]