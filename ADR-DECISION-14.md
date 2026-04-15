### ADR-14: Implement CRUD functionality without access restriction

**Author:** Melanie Bardoux

**Status:** Accepted

**AI Usage:**  
Claude AI used to identify required changes and assist with code implementation.

**Context:**  
The site requires CRUD functionality as part of the assessment criteria. Edit and Delete views have been implemented for the Recording model. However, without a formal authentication and authorisation system in place, these views are currently accessible to any user.

**Alternatives considered:**  

- Option 1: Restrict edit and delete to admin only via Django's built-in permissions, not feasible without a proper login system in place.

- Option 2: Implement full authorisation now - out of scope for Assessment 2

**Decision:**  
Implement Edit and Delete views for Recording to meet CRUD requirements. Delete/edit access restriction will be implemented with a formal authentication system in Assessment 4.

**Code reference:**  
group11_app/views.py — RecordingUpdateView, RecordingDeleteView
group11_app/templates/recordings/recording_confirm_delete.html
group11_project/urls.py

**Consequences:**  
Edit and delete are currently unrestricted and must be secured in Assessment 4 when authentication is implemented.