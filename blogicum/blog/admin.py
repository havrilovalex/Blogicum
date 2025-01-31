from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from constants import ADMIN_TEXT_LENGTH
from .models import Category, Comment, Location, Post


@admin.display(description="Текст")
def short_version_text(obj):
    return f"{obj.text}"[:ADMIN_TEXT_LENGTH] + '...'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    empty_value_display = 'Не задано'
    list_display = (
        'title',
        short_version_text,
        'is_published',
        'author',
        'pub_date',
        'created_at',
        'category',
        'image',
    )
    list_editable = (
        'is_published',
    )
    search_fields = ('title',)
    list_filter = ('category',)
    list_display_links = ('title',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'description',
        'created_at',
        'is_published',
    )
    list_editable = (
        'is_published',
    )


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'created_at',
        'is_published',
    )
    list_editable = (
        'is_published',
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'link_to_author',
        short_version_text,
        'created_at',
        'is_published',
        'link_to_post',
    )
    list_editable = (
        'is_published',
    )
    search_fields = ('post__title',)
    list_filter = ('post',)
    list_display_links = (short_version_text,)

    def link_to_post(self, obj):
        post = obj.post
        if post:
            url = reverse(
                "admin:blog_post_change",
                args=(post.pk,)
            )
            return format_html('<a href="{}">{}</a>', url, post)
        return "-"

    link_to_post.short_description = "Ссылка на пост"

    def link_to_author(self, obj):
        author = obj.author
        if author:
            url = reverse(
                "admin:auth_user_change",
                args=(author.pk,)
            )
            return format_html('<a href="{}">{}</a>', url, author)
        return "-"

    link_to_author.short_description = "Ссылка на автора"
