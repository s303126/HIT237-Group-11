### ADR-18: Custom StaffRequiredMixin and role-based permission strategy

**Date:** 21/05/26

**Author:** Melanie Bardoux

**Status:** Accepted | Supersedes ADR-14

**AI Usage:**  
Claude AI used to assist with identifying permission requirements across views. Implementation and integration decisions by Melanie Bardoux.

**Context:**  
The site has two user roles (researcher and citizen_scientist) in addition to anonymous users, requiring different levels of access. All users need clearly defined permissions to ensure the site functions appropriately and data is protected.

**Alternatives considered:**  

- Option 1: Custom StaffRequiredMixin checking the role field on the custom User model. Straightforward to implement and directly references the role field already defined on the User model.

- Option 2:  Django's built-in UserPassesTestMixin or PermissionRequiredMixin. More flexible but relies on Django's permission framework which is not aligned with the custom role field on the User model.

**Decision:**  
Implement two custom mixins to enforce role-based access across views. LoginRequiredMixin restricts submission and flagging to authenticated users (citizen scientists). StaffRequiredMixin restricts edit, delete and anomaly resolution to researchers. Permissions are applied as follows:

- Anonymous users: read access only (species list, species detail, recording list, recording detail)

- Authenticated users: submit recordings, flag anomalies

- Researchers only: edit recordings, delete recordings, resolve anomalies

- Anomaly resolution — restricted to researchers or the user who originally flagged the anomaly

**Code reference:**  
accounts/mixins.py
group11_app/views.py (LoginRequiredMixin and StaffRequiredMixin applied to views)

**Consequences:**  
Access is restricted based on user role. Anonymous users retain read access to the site. The custom mixin is reusable across any view that requires researcher access. Future consideration: researcher role is currently self-selected at registration and has no verification process.