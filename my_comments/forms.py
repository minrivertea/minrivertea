from django import forms
from django.contrib.comments.forms import CommentForm

from captcha.fields import CaptchaField

class CustomCommentForm(CommentForm):
    captcha = CaptchaField()
    