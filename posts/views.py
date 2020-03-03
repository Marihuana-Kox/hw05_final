from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from django.contrib import messages
from django.contrib.auth.models import User
from .models import Post, Group, Comment, Follow
from .forms import PostForm, CommentForm

from django.views.decorators.cache import cache_page
from django.http import request

from collections import Counter


@cache_page(20)
def index(request):
    post_list = Post.objects.order_by("-pub_date").all()
    # показывать по 10 записей на странице.
    paginator = Paginator(post_list, 8)
    # переменная в URL с номером запрошенной страницы
    page_number = request.GET.get('page')
    # получить записи с нужным смещением
    page = paginator.get_page(page_number)
    return render(request, 'posts/index.html', {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group)
    paginator = Paginator(post_list.order_by("-pub_date"), 8)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "posts/group.html", {"group": group, "page": page, "paginator": paginator})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    count_author = Follow.objects.filter(author=author).count()
    count_user = Follow.objects.filter(user=author).count()
    post_user_list = Post.objects.filter(author=author)
    count = post_user_list.count()
    following = False
    if Follow.objects.filter(user=request.user, author=author).exists():
        following = True
    paginator = Paginator(post_user_list.order_by("-pub_date"), 8)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "posts/profile.html", {"page": page, "author": author, "count": count, "paginator": paginator, "following": following, "count_author": count_author, "count_user": count_user})


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    author = User.objects.get(username=username)
    count_author = Follow.objects.filter(author=author).count()
    count_user = Follow.objects.filter(user=author).count()
    following = False
    if Follow.objects.filter(user=request.user, author=author).exists():
        following = True
    count = Post.objects.filter(author=author).count()
    items = Comment.objects.filter(post_id=post.pk)
    form = CommentForm()
    return render(request, "posts/post.html", {"items": items, "form": form, "post": post, "count": count, "username": author, "following": following, "count_author": count_author, "count_user": count_user})


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def delete_post(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    author = get_object_or_404(User, username=username)
    post.delete()
    messages.success(
        request, "Ваше пост удален!", extra_tags='', fail_silently=False)
    return redirect("profile", username=author)


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    author = get_object_or_404(User, username=username)
    if request.method == "POST":
        form = PostForm(request.POST or None,
                        files=request.FILES or None, instance=post)
        if form.is_valid():
            post = form.save()
            form.author = request.user
            if form.save():
                messages.success(
                    request, "Ваше сообщение отредактировано!", extra_tags='', fail_silently=False)
            else:
                messages.success(request, "Ошибка редактиорования!",
                                 extra_tags='', fail_silently=False)
            return redirect("post", username=author, post_id=post.pk)
        else:
            messages.success(request, "Валидация формы не прошла!",
                             extra_tags='', fail_silently=False)
            return redirect("post", username=author, post_id=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, "posts/post_edit.html", {"form": form, "post": post})


@login_required
def new_post(request):
    if request.method == "POST":
        form = PostForm(request.POST or None,
                        files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.text = form.cleaned_data["text"]
            post.group = form.cleaned_data["group"]
            post.author = request.user
            post.save()
            return redirect("/")
    else:
        form = PostForm()
    return render(request, "posts/new.html", {"form": form})


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    author = get_object_or_404(User, username=username)
    count = Post.objects.filter(author=author).count()
    if request.method == "POST":
        form = CommentForm(request.POST or None)
        if form.is_valid():
            form = form.save(commit=False)
            form.post = post
            form.author = request.user
            form.save()
            messages.success(
                request, "Ваш комментарий добавлен!", extra_tags='', fail_silently=False)
            return redirect("post", username=author, post_id=post.pk)
    else:
        form = CommentForm()
    return render(request, "posts/post.html", {"form": form, "post": post, "count": count, "username": author})


@login_required
def follow_index(request):
    follow = Follow.objects.filter(user=request.user)
    author_list = [favorite.author for favorite in follow]
    post_list = Post.objects.filter(author__in=author_list)
    paginator = Paginator(post_list.order_by("-pub_date"), 8)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "posts/follow.html", {"page": page, "paginator": paginator})


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    dbll = Follow.objects.filter(user=request.user, author=author).count()
    if author != request.user and dbll == 0:
        user = Follow(user=request.user, author=author)
        user.save()
    return redirect("follow_index")


@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    author_by = get_object_or_404(Follow, user=request.user, author=author)
    author_by.delete()
    return redirect("follow_index")
