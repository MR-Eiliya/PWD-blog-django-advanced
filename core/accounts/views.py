from django.contrib.auth import (
    login,
    authenticate,
    get_user_model,
)
from .forms import (
    CustomLoginForm,
    CustomUserCreationForm,
)
from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.views import LogoutView

User = get_user_model()

class AuthView(View):
    template_name = "accounts/auth.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("website:index")
        
        return render(request, self.template_name,{
            "login_form": CustomLoginForm(),
            "register_form": CustomUserCreationForm(),
        })
    

    def post(self, request):
        if "login_submit" in request.POST:
            return self.handle_login(request)
        elif "register_submit" in request.POST:
            return self.handle_register(request)
        
        return redirect("accounts:auth")
    

    def handle_login(self, request):
        login_form = CustomLoginForm(request.POST)
        register_form = CustomUserCreationForm()

        if login_form.is_valid():
            identifier = login_form.cleaned_data["identifier"]
            password = login_form.cleaned_data["password"]

            if "@" in identifier:
                user_obj = User.objects.filter(email=identifier).first()
            else:
                user_obj = User.objects.filter(username=identifier).first()

            if user_obj:
                user = authenticate(
                    request,
                    username=user_obj.email, 
                    password=password
                )

                if user:
                    login(request, user)
                    messages.success(request, "Welcome Back!")
                    return redirect("website:index")

            login_form.add_error(None, "Invalid credentials")

        return render(request, self.template_name, {
            "login_form": login_form,
            "register_form": register_form,
        })
    

    def handle_register(self, request):
        register_form = CustomUserCreationForm(request.POST)
        login_form = CustomLoginForm()


        if register_form.is_valid():
            user = register_form.save()
            login(request, user)
            messages.success(request, "your account created successfully!")
            return redirect("website:index")
        
        return render(request, self.template_name, {
            "login_form": login_form,
            "register_form": register_form,
        })
    


class CustomLogoutView(LogoutView):
    next_page = "/"