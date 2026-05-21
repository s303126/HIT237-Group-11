from django.http import HttpResponseForbidden

class StaffRequiredMixin:
    """
    Mixin that requires user to be staff (researcher role).
    Returns 403 Forbidden if user is not staff.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("You must be logged in to access this page.")
        if not request.user.role == 'researcher':
            return HttpResponseForbidden("You do not have permission to access this page. Researcher access required.")
        return super().dispatch(request, *args, **kwargs)