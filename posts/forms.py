from django import forms
from . models import *


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {'text': 'Текст сообщения', 'group': 'Группа'}
        widgets = {'text': forms.Textarea(
            attrs={'cols': 80, 'rows': 10, 'placeholder': 'Здесь пишите свой текст'})}


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': 'Текст сообщения'}
        widgets = {'text': forms.Textarea(
            attrs={'cols': 80, 'rows': 10, 'placeholder': 'Здесь пишите свой комментарий'})}
