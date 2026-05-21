### ADR-17: Create separate accounts app and remove guest user workaround

**Date:** 21/05/2026

**Author:** Melanie Bardoux

**Status:** Accepted | Supersedes ADR-14 (partial)

**AI Usage:**  
AI used to assist with identifying appropriate structure for implementing second app. Implementation and integration decisions by Melanie Bardoux.

**Context:**  
The site required an authentication system to replace the guest user workaround and to support role-based access and restrictions. A decision was needed on whether to add authentication logic directly to group11_app or in a separate app.

**Alternatives considered:**  

- Option 1: Create a separate accounts app for authentication logic. Follows Django conventions for separating concerns and keeps group11_app focused on species and recording functionality.

- Option 2: Add authentication directly to group11_app. Less setup required, but mixes authentication logic with core application logic and makes the codebase harder to maintain.

**Decision:**  
Create a separate accounts app to house all authentication logic including URLs, views, forms, templates and mixins. The guest user workaround was removed as it is no longer needed once a proper authentication system is in place.

**Code reference:**  
accounts/urls.py
accounts/views.py
accounts/forms.py
accounts/templates/accounts/
group11_project/settings.py (accounts added to INSTALLED_APPS)
group11_project/urls.py (accounts URLs included)
group11_app/views.py (guest user logic removed)


**Consequences:**  
Authentication logic is isolated from core application logic. The guest user workaround referenced in ADR-14 is now removed. All form submissions now require an authenticated user. The accounts app can be extended in future without affecting group11_app.