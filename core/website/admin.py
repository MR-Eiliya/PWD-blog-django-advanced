from django.contrib import admin
from .models import Contact

class ContactAdmin(admin.ModelAdmin):
    list_display = [
        "first_name",
        "last_name",
        "email",
        "message",
        "created_date",
        "updated_date",
    ]


admin.site.register(Contact)
