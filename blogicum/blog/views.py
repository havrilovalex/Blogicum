from django.contrib.auth.mixins import (
    LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin)
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView)


from blog.forms import CommentForm, PostForm, UserUpdateForm
from blog.models import Category, Comment, Post, User
from blog.utils import detailed_post_permission, get_post_info
from constants import QNT_POSTS_ON_MAIN


class OnlyAuthorMixin(UserPassesTestMixin):
    """Миксин для проверки авторства для доступа к действию."""

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user

    def handle_no_permission(self):
        return redirect('blog:post_detail', pk=self.kwargs['pk'])


class IndexListView(ListView):
    """Класс представления главной страницы со списком всех публикаций."""

    model = Post
    template_name = 'blog/index.html'
    paginate_by = QNT_POSTS_ON_MAIN

    def get_queryset(self):
        res = get_post_info(
            self.model
        ).order_by('-pub_date').annotate(comment_count=Count('comments'))
        return res


class PostDetailView(PermissionRequiredMixin, DetailView):
    """Класс представления страницы с полным текстом данной публикации."""

    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.all()
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
        queryset = get_post_info(self.model).filter(
            category=self.current_category
        ).order_by('-pub_date').annotate(comment_count=Count('comments'))
        return queryset

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
        res = Post.objects.filter(
            author=self.user
        ).order_by('-pub_date').annotate(
            comment_count=Count('comments')
        )
        return res

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.user
        return context


class ProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Класс представления для редактирования данных пользователя."""

    model = User
    form_class = UserUpdateForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def test_func(self):
        profile_owner = self.get_object()
        return self.request.user.username == profile_owner.username

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
        form.files = self.request.FILES
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()
        return super().form_valid(form)

    def get_success_url(self):
        res = reverse(
            'blog:profile',
            kwargs={'user_name': self.request.user.username}
        )
        return res


class PostUpdateView(OnlyAuthorMixin, UpdateView):
    """Класс представления редактирования публикации."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.get_object().id})


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    """Класс представления удаления публикации."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()

        form = PostForm(instance=post)
        for field in form.fields:
            form.fields[field].widget.attrs['disabled'] = True

        context['form'] = form
        context['is_delete'] = True
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
        post = get_object_or_404(Post, pk=self.kwargs['pk'])

        comment = form.save(commit=False)
        comment.post = post
        comment.author = self.request.user
        comment.save()

        return redirect('blog:post_detail', pk=post.pk)


class CommentUpdateView(OnlyAuthorMixin, UpdateView):
    """Класс представления редактирования комментария."""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):
        res = get_object_or_404(Comment, pk=self.kwargs['comment_id'])
        return res

    def get_success_url(self):
        res = reverse(
            'blog:post_detail',
            kwargs={'pk': self.get_object().post.pk}
        )
        return res


class CommentDeleteView(OnlyAuthorMixin, DeleteView):
    """Класс представления удаления комментария."""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):
        res = get_object_or_404(Comment, pk=self.kwargs['comment_id'])
        return res

    def get_success_url(self):
        res = reverse(
            'blog:post_detail',
            kwargs={'pk': self.get_object().post.pk}
        )
        return res
