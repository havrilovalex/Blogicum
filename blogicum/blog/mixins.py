from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect


class OnlyAuthorMixin(UserPassesTestMixin):
    """Миксин для проверки авторства для доступа к действию."""

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user

    def handle_no_permission(self):
        return redirect('blog:post_detail', pk=self.kwargs['pk'])
