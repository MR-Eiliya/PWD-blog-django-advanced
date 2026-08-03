from django import forms
from .models import Post, Comment

class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ["title", "content", "image", "status", "category", "published_date"]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "style": "background:#2b2b2b;color:white;border:none;"
            }),

            "content": forms.Textarea(attrs={
                "class": "form-control",
                "style": "background:#2b2b2b;color:white;border:none;"
            }),

            "category": forms.Select(attrs={
                "class": "form-control",
                "style": "background:#2b2b2b;color:white;border:none;"
            }),

            "published_date": forms.DateTimeInput(attrs={
                "class": "form-control",
                "style": "background:#2b2b2b;color:white;border:none;",
                "type": "datetime-local"
            }),

            "status": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
        }



class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ["name", "email", "message"]


class CommentReplyForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["message"]
