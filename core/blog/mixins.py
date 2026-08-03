from django.http import Http404


class AdminOnlyMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            raise Http404()
        return super().dispatch(request, *args, **kwargs)
    


class AuthorRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        
        if not request.user.is_authenticated:
            raise Http404()
        
        post = self.get_object()

        try:
            profile = request.user.profile

        except:
            raise Http404()
        
        if post.author != profile:
            raise Http404()
        
        return super().dispatch(request, *args, **kwargs)
