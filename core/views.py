from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import Profile, Post, LikePost, FollowersCount
from django.contrib.auth.decorators import login_required
from itertools import chain

# Create your views here.

@login_required(login_url='signin')
def index(req):
    user_object = User.objects.get(username=req.user.username)
    user_profile = Profile.objects.get(user=user_object)
    
    user_following_list = []
    feed = []
    
    user_following = FollowersCount.objects.filter(follower=req.user.username)
    
    for users in user_following:
        user_following_list.append(users.user)
        
    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user = usernames)
        feed.append(feed_lists)
    
    feed_lists = list(chain(*feed))
    
    posts = Post.objects.all()
    
    return render(req, 'index.html',{'user_profile': user_profile, 'posts':feed_lists})

def signup(req):
    if req.method=='POST':
        username = req.POST['username']
        email = req.POST['email']
        password = req.POST['password']
        password2 = req.POST['password2']
        
        if password==password2:
            if User.objects.filter(email=email).exists():
                messages.info(req, 'Email Taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(req, 'Username Taken')
                return redirect('signup')
            else:
                user=User.objects.create_user(username=username, email=email, password=password)
                user.save()
                
                #log user in and direct to the settings page
                user_login = auth.authenticate(username=username, password=password)
                auth.login(req,user_login)
                
                #create a profile object for the new user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('settings')
        else:
            messages.info(req, 'Password not matching')
            return  redirect('signup')
        
    else:
        return render(req, 'signup.html')

def signin(req):
    if req.method=='POST':
        username=req.POST['username']
        password=req.POST['password']
        
        user=auth.authenticate(username=username, password=password)
        
        if user is not None:
            auth.login(req,user)
            return redirect('/')
        else:
            messages.info(req, "Credentials Invalid")
            return redirect('signin')
    else:
        return render(req, 'signin.html')
    
@login_required(login_url='signin')    
def logout(req):
    auth.logout(req)
    return redirect('signin')

@login_required(login_url='signin')   
def settings(req):
    user_profile = Profile.objects.get(user=req.user)
    
    if req.method=='POST':
        if req.FILES.get('image')==None:
            image = user_profile.profileimg
            bio=req.POST['bio']
            location=req.POST['location']

            user_profile.profileimg=image
            user_profile.bio=bio
            user_profile.location=location
            user_profile.save()
            
        if req.FILES.get('image')!=None:
            image = req.FILES.get('image')
            bio=req.POST['bio']
            location=req.POST['location']

            user_profile.profileimg=image
            user_profile.bio=bio
            user_profile.location=location
            user_profile.save()
        return redirect('settings')
        
    return render(req,"setting.html",{'user_profile':user_profile})

@login_required(login_url='signin') 
def upload(req):
    if req.method=='POST':
        user = req.user.username
        image = req.FILES.get('image_upload')
        caption = req.POST['caption']
        
        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()
        
        return redirect('/')
    else:
        return redirect('/')
    
@login_required(login_url='signin') 
def like_post(req):
    username = req.user.username
    post_id = req.GET.get('post_id')
    
    post = Post.objects.get(id=post_id)
    
    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first() #incase its already liked
    
    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        
        post.no_of_likes = post.no_of_likes+1
        post.save()
        
    else:
        like_filter.delete()
        post.no_of_likes = post.no_of_likes-1
        post.save()
    
    return redirect('/')
        
@login_required(login_url='signin') 
def profile(req, pk):
    user_object=User.objects.get(username=pk)
    user_profile=Profile.objects.get(user=user_object)
    user_posts=Post.objects.filter(user=pk)
    user_post_length=len(user_posts)
    
    follower = req.user.username
    user=pk
    
    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'
    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))
    
    context={
        'user_object':user_object,
        'user_profile':user_profile,
        'user_post_length':user_post_length,
        'user_posts':user_posts,
        'button_text':button_text,
        'user_following':user_following,
        'user_followers':user_followers,
    }
    
    return render(req,'profile.html',context)

@login_required(login_url='signin') 
def follow(req):
    if req.method == 'POST':
        follower = req.POST['follower']
        user = req.POST['user']
        
        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/'+user)
        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/'+user)
    else:
        return redirect('/')
    