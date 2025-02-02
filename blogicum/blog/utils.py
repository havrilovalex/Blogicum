from django.db.models import Count
from django.utils.timezone import now

from blog.models import Post


def get_post_info(
    post_model=Post.objects,
    apply_default_filters=True,
    order_by_pub_date=True,
    annotate_comments=True
):
    """
    Возвращает запрос к БД для Post модели.

    Аргументы:
        post_model: класс модели поста.
        apply_default_filters: фильтры опубликованной модели при True.
        order_by_pub_date: Отсортировать по `-pub_date` при True.
        annotate_comments: аннотация `comment_count` если True.
    """
    queryset = post_model.select_related(
        'category', 'location', 'author')

    if apply_default_filters:
        queryset = queryset.filter(
            is_published=True,
            pub_date__lt=now(),
            category__is_published=True
        )

    if order_by_pub_date:
        queryset = queryset.order_by('-pub_date')

    if annotate_comments:
        queryset = queryset.annotate(comment_count=Count('comments'))

    return queryset


def detailed_post_permission(self):
    """
    Функция определения доступа к странице публикации.

    Доступ разрешен либо автору, либо всем остальным пользователям при условии
    опубликованной модели (PublishableModel).
    """
    permission = (
        (self.request.user == self.get_object().author
         ) or (
            (self.get_object().is_published)
            and (self.get_object().category.is_published)
            and (self.get_object().pub_date <= now())
        )
    )
    return permission
