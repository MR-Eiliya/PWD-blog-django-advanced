from django.views.generic import TemplateView, CreateView
from django.http import HttpResponseRedirect
from .forms import ContactForm
from .models import Contact
from django.urls import reverse_lazy
from blog.models import Post


class IndexView(TemplateView):
    template_name = "website/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hero_index"] = (
            "Explore web development, design, SEO, and e-commerce insights, discover practical tips, and learn how to turn your ideas into real digital experiences."
        )

        context["posts"] = (
            Post.objects.filter(status=True)
            .order_by("-published_date")[:3]
        )
        return context


class AboutView(TemplateView):
    template_name = "website/about.html"


class ContactView(CreateView):
    
    model = Contact
    form_class = ContactForm
    template_name = "website/contact.html"
    success_url = reverse_lazy("website:contact")

    
    def form_valid(self, form):
        print("Form is valid. Attempting to save.")
        return super().form_valid(form)
   
    
    def form_invalid(self, form):
        print("❌ form_invalid: errors =", form.errors)
        return super().form_invalid(form)
   

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context["address"] = ("Iran, Street of Freedom")
        context["phone"] = ("+989136358518")
        context["email"] = ("shahin.it.org@gmail.com")
        return context