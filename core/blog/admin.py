from django.contrib import admin
from .models import Post, Category, Comment


class PostAdmin(admin.ModelAdmin):
    list_display = [
        "author",
        "title",
        "status",
        "category",
        "created_date",
        "published_date",
    ]


class CommentAdmin(admin.ModelAdmin):
    list_display = [
        "post",
        "name",
        "email",
        "message",
        "created_date",
        "updated_date",
    ]
    list_filter = (
        "email",
        "name",
        
    )

admin.site.register(Post)
admin.site.register(Category)
admin.site.register(Comment)