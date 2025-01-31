from django import forms
from django.forms import DateTimeInput
from .models import Comment, Post, User


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ['author', 'is_published']
        widgets = {
            'pub_date': DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                }
            ),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text', ]


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
        ]
