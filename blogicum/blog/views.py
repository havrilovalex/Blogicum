from django.contrib.auth.mixins import (
    LoginRequiredMixin, PermissionRequiredMixin)
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.timezone import now
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView)

from blog.forms import CommentForm, PostForm, UserUpdateForm
from blog.mixins import OnlyAuthorMixin
from blog.models import Category, Comment, Post, User
from blog.utils import detailed_post_permission, get_post_info
from constants import QNT_POSTS_ON_MAIN


class IndexListView(ListView):
    """Класс представления главной страницы со списком всех публикаций."""

    model = Post
    template_name = 'blog/index.html'
    paginate_by = QNT_POSTS_ON_MAIN

    def get_queryset(self):
        return get_post_info()


class PostDetailView(PermissionRequiredMixin, DetailView):
    """Класс представления страницы с полным текстом данной публикации."""

    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author').all()
        )
        return context

    def has_permission(self):
        flag = detailed_post_permission(self)
        return flag

    def handle_no_permission(self):
        raise Http404()


class CategoryListView(ListView):
    """Класс представления для отображения списка публикаций в категории."""

    model = Post
    template_name = 'blog/category.html'
    paginate_by = QNT_POSTS_ON_MAIN

    def get_queryset(self):
        self.current_category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return get_post_info(self.current_category.posts.all())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_category'] = self.current_category
        return context


class ProfileListView(ListView):
    """Класс представления страницы профиля."""

    model = Post
    template_name = 'blog/profile.html'
    paginate_by = QNT_POSTS_ON_MAIN

    def get_queryset(self):
        self.user = get_object_or_404(User, username=self.kwargs['user_name'])
        res = get_post_info(
            self.user.posts.all(),
            apply_default_filters=self.request.user != self.user
        )
        return res

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.user
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Класс представления для редактирования данных пользователя."""

    model = User
    form_class = UserUpdateForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        res = reverse(
            'blog:profile',
            kwargs={'user_name': self.request.user.username}
        )
        return res


class PostCreateView(LoginRequiredMixin, CreateView):
    """Класс представления создания публикации."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        res = reverse(
            'blog:profile',
            kwargs={'user_name': self.request.user.username}
        )
        return res


class PostUpdateView(LoginRequiredMixin, OnlyAuthorMixin, UpdateView):
    """Класс представления редактирования публикации."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.get_object().id})


class PostDeleteView(LoginRequiredMixin, OnlyAuthorMixin, DeleteView):
    """Класс представления удаления публикации."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()

        form = PostForm(instance=post)
        context['form'] = form
        return context

    def get_success_url(self):
        res = reverse(
            'blog:profile',
            kwargs={'user_name': self.request.user.username}
        )
        return res


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Класс представления создания комментария."""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        self.post = get_object_or_404(Post, pk=self.kwargs['pk'])
        form.instance.post = self.post
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        res = reverse(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['pk']}
        )
        return res


class CommentUpdateView(LoginRequiredMixin, OnlyAuthorMixin, UpdateView):
    """Класс представления редактирования комментария."""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        res = reverse(
            'blog:post_detail',
            kwargs={'pk': self.get_object().post.pk}
        )
        return res


class CommentDeleteView(LoginRequiredMixin, OnlyAuthorMixin, DeleteView):
    """Класс представления удаления комментария."""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        res = reverse(
            'blog:post_detail',
            kwargs={'pk': self.get_object().post.pk}
        )
        return res
