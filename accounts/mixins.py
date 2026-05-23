from django.http import HttpResponseForbidden

class StaffRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("You must be logged in to access this page.")
        if not request.user.has_researcher_access():
            return HttpResponseForbidden(
                "You do not have permission to access this page. Approved researcher access required."
            )
        return super().dispatch(request, *args, **kwargs)