from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = "website/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hero_index"] = (
            "Explore web development, design, SEO, and e-commerce insights, discover practical tips, and learn how to turn your ideas into real digital experiences."
        )
        return context


class AboutView(TemplateView):
    template_name = "website/about.html"


class ContactView(TemplateView):
    template_name = "website/contact.html"