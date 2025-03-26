from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from .models import BlogPost, Comment, UserProfile
from .forms import BlogPostForm, CommentForm, UserProfileForm

# Create your views here.

def home(request):
    return render(request, 'myapp/home.html')

def blog_list(request):
    # Get all blog posts ordered by creation date (newest first)
    blog_posts = BlogPost.objects.all().order_by('-created_at')
    
    # Paginate the blog posts (5 per page)
    paginator = Paginator(blog_posts, 5)
    
    # Get the page number from the request
    page_number = request.GET.get('page')
    
    # Get the page object
    page_obj = paginator.get_page(page_number)
    
    context = {
        'blog_posts': page_obj,
        'is_paginated': True,
        'page_obj': page_obj,
    }
    
    return render(request, 'myapp/blog_list.html', context)

def blogger_detail(request, user_id):
    blogger = get_object_or_404(User, id=user_id)
    posts = BlogPost.objects.filter(author=blogger).order_by('-created_at')
    return render(request, 'myapp/blogger_detail.html', {
        'blogger': blogger,
        'posts': posts
    })

def blogger_list(request):
    bloggers = User.objects.filter(blogpost__status='published').distinct().annotate(
        post_count=Count('blogpost', filter=Q(blogpost__status='published'))
    ).order_by('-post_count')
    return render(request, 'myapp/blogger_list.html', {'bloggers': bloggers})

def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    comments = post.comments.all()
    return render(request, 'myapp/blog_detail.html', {'post': post, 'comments': comments})

@login_required
def delete_blog_post(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    
    # Check if the user is the author of the post
    if post.author != request.user:
        messages.error(request, 'You do not have permission to delete this post.')
        return redirect('blogger_detail', user_id=post.author.id)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Blog post deleted successfully!')
        return redirect('blogger_detail', user_id=request.user.id)
    
    return render(request, 'myapp/delete_blog_post.html', {'post': post})

@login_required
def create_blog_post(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Blog post created successfully!')
            return redirect('blog_detail', slug=post.slug)
    else:
        form = BlogPostForm()
    return render(request, 'myapp/blog_form.html', {'form': form, 'title': 'Create New Post'})

@login_required
def edit_blog_post(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    if post.author != request.user:
        messages.error(request, 'You can only edit your own posts.')
        return redirect('blog_detail', slug=slug)
    
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Blog post updated successfully!')
            return redirect('blog_detail', slug=slug)
    else:
        form = BlogPostForm(instance=post)
    return render(request, 'myapp/blog_form.html', {'form': form, 'title': 'Edit Post'})

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('register')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')

        if len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password1)
        login(request, user)
        messages.success(request, 'Registration successful!')
        return redirect('home')

    return render(request, 'myapp/register.html')

@login_required
def create_comment(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Comment added successfully!')
            return redirect('blog_detail', slug=slug)
    else:
        form = CommentForm()
    return render(request, 'myapp/comment_form.html', {'form': form, 'post': post})

@login_required
def like_post(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    return JsonResponse({
        'liked': liked,
        'likes_count': post.get_likes_count()
    })

@login_required
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
        liked = False
    else:
        comment.likes.add(request.user)
        liked = True
    return JsonResponse({
        'liked': liked,
        'likes_count': comment.get_likes_count()
    })

@login_required
def share_post(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    post.shares += 1
    post.save()
    return JsonResponse({
        'shares_count': post.shares
    })

@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    user_profile, created = UserProfile.objects.get_or_create(user=user_to_follow)
    
    if request.user == user_to_follow:
        return JsonResponse({
            'error': 'You cannot follow yourself'
        }, status=400)
    
    if request.user in user_profile.followers.all():
        user_profile.followers.remove(request.user)
        following = False
    else:
        user_profile.followers.add(request.user)
        following = True
    
    return JsonResponse({
        'following': following,
        'followers_count': user_profile.get_followers_count()
    })

@login_required
def edit_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('blogger_detail', user_id=request.user.id)
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'myapp/edit_profile.html', {'form': form})

@login_required
def followers_list(request, user_id):
    user = get_object_or_404(User, id=user_id)
    followers = user.profile.followers.all()
    return render(request, 'myapp/followers_list.html', {
        'user': user,
        'followers': followers
    })

@login_required
def following_list(request, user_id):
    user = get_object_or_404(User, id=user_id)
    following = user.following.all()
    return render(request, 'myapp/following_list.html', {
        'user': user,
        'following': following
    })

def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('blogger_detail', user_id=user.id)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'myapp/login.html')
