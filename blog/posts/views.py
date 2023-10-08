from django.db.models import Count, Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from marketing.models import Subscribe
from posts.forms import CommentForm
from posts.models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def get_category_count():
    queryset = Post.objects.values('categories__title').annotate(Count('categories__title'))
    return queryset


def search(request):
    queryset = Post.objects.all()
    query = request.GET.get('q')
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) |
            Q(overview__icontains=query)
        ).distinct()
    context = {
        "queryset": queryset,

    }
    return render(request, "search_results.html", context)


def index(request):
    featured = Post.objects.filter(featured=True)
    latest = Post.objects.order_by('-timestamp')[0:3]
    context = {
        'object_list': featured,
        'latest': latest,
    }

    if request.method == "POST":
        email = request.POST['email']
        new_subscribe = Subscribe()
        new_subscribe.email = email
        new_subscribe.save()

    return render(request, 'index.html', context)


def blog(request):
    most_recent = Post.objects.order_by('-timestamp')[:3]
    category_count = get_category_count()
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 1)
    page_request_var = 'page'
    page = request.GET.get(page_request_var)
    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger:
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        paginated_queryset = paginator.page(paginator.num_pages)

    context = {
        "queryset": paginated_queryset,
        "page_request_var": page_request_var,
        "most_recent": most_recent,
        "category_count": category_count,
    }
    return render(request, 'blog.html', context)


def post(request, id):
    category_count = get_category_count()
    most_recent = Post.objects.order_by('-timestamp')[:3]
    post = get_object_or_404(Post, id=id)
    form = CommentForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.instance.user = request.user
            form.instance.post = post
            form.save()
            return redirect(reverse("post_detail", kwargs={
                'id': post.pk
            }))

    context = {
        'post': post,
        'most_recent': most_recent,
        'category_count': category_count,
        'form':form,
    }
    return render(request, 'post.html', context)

