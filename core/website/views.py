from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = "website/index.html"


class AboutView(TemplateView):
    pass


class ContactView(TemplateView):
    pass