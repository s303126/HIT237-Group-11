### ADR-19: Self-selection of researcher role requires admin approval

**Date:** 23/05/2026

**Author:** Melanie Bardoux

**Status:** Accepted 

**AI Usage:** Claude AI used to identify the approach and assist with implementation.

**Context:**  
Users can self-select the researcher role during signup, which immediately grants elevated permissions such as editing and deleting recordings. This means any user could gain researcher-level access without verification, undermining the integrity of the data moderation system

**Alternatives considered:**  

- Option 1: Remove researcher from the signup form and have admins create researcher accounts manually - secure but creates unnecessary admin overhead and poor user experience

- Option 2: Maintain a pre-approved list of researcher emails so that users on the list are automatically granted researcher access on signup. This is straightforward but requires the list to be maintained and updated, and new researchers cannot be added without admin intervention ahead of time.

- Option 3: Add an is_approved boolean field so users can request researcher status but only gain permissions after admin approval. This is simple, requires no additional infrastructure, and integrates with the existing admin panel.

**Decision:**
Added an is_approved field to the User model, defaulting to False. The StaffRequiredMixin and AnomalyResolveView now check both role and approval status using a has_researcher_access method on the User model. Admins can approve researchers individually or in bulk through the Django admin panel. Unapproved researchers see a "Pending" indicator in the navigation bar and only have basic user permissions until admin approval.

**Code reference:**
group11_app/models.py: User.is_approved field, User.has_researcher_access()
accounts/mixins.py: StaffRequiredMixin
group11_app/views.py: AnomalyResolveView
group11_app/admin.py: UserAdmin with list_editable and approve_researchers action
group11_app/templates/base.html: pending status displa

**Consequences:**
Users who select researcher at signup are given citizen scientist permissions until approved. Existing researcher accounts created before this change will need to be manually approved via admin. Without this system any user could self-select researcher at signup and immediately gain access to edit or delete other user's data. Group members must run migrations after pulling this change.