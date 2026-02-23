from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class CustomLoginForm(forms.Form):
    identifier = forms.CharField(
        label="Username or Email",
        max_length=255,
        widget=forms.TextInput(attrs={"autofocus": True}),
    )    
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput,
    )



class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = CustomUser(
            email=self.cleaned_data["email"],
            username=self.cleaned_data["username"],
        )
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()

        return user