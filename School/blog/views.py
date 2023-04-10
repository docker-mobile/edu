from django.shortcuts import render, redirect, get_object_or_404
from .models import Post
from .forms import PostForm

# Create your views here.
def blog(request):
    if request.GET.get('page'):
        page = request.GET.get('page')
        posts = Post.objects.all()[page-1*5:page*5]
    else:
        posts = Post.objects.all()[0:5]
    categories = []
    for post in Post.objects.all():
        categories.append(post.category)
    context = {
        'title': 'وبلاگ',
        'posts': posts,
        'categories': categories,
        'famous_post': Post.objects.all().order_by('-view')[:5],
    }
    return render(request, 'blog/blog.html', context)

def blog_view(request, slug):
    post = Post.objects.get(slug=slug)
    post.view += 1
    post.save()
    context = {
        'title': post.title,
        'post': post,
    }
    return render(request, "blog/view post.html", context)

def blog_edit_view(request, slug):
    post = get_object_or_404(Post, slug=slug)
    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    context = {
        'title': 'ویرایش',
        'form': form,
    }
    return render(request, 'blog/post edit.html', context)
def blog_delete_view(slug):
    post = get_object_or_404(Post, slug=slug)
    post.delete()
    return redirect('/blog/')