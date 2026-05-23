### ADR-20: Object-level permissions for recording edit and delete

**Date:** 23/05/26

**Author:** Melanie Bardoux

**Status:** Accepted 

**AI Usage:** Claude AI used to assist with mixin implementation. Design decision made by Melanie Bardoux based on the need for granular access control beyond role-based permissions

**Context:**  
ADR-18 established role-based access where only researchers could edit or delete recordings. This meant citizen scientists could not edit or delete their own submissions.

AnomalyResolveView already used object-level checks to allow the original flagger or a researcher to resolve an anomaly. The OwnerOrStaffRequiredMixin formalises this pattern into a reusable component for recording edit and delete views.

**Alternatives considered:**  

- Option 1: Keep role-based only and have researchers handle all edits on behalf of users. Simple but removes user autonomy and creates unnecessary workload for researchers.

- Option 2: Option 2: Check ownership in each view individually. Works but duplicates logic across views, which violates Django's DRY principle and is easy to overlook when adding new views.

- Option 3: Create a reusable OwnerOrStaffRequiredMixin that checks whether the user owns the object or is an approved researcher. Centralises the logic in one place and can be applied to any view with an object owner.


**Decision:**  
Created a reusable OwnerOrStaffRequiredMixin that checks whether the logged in user owns the recording or is an approved researcher. If neither condition is met, access is denied. This mixin replaces StaffRequiredMixin on the edit and delete views. The edit and delete buttons are also hidden in the template for users without permission, so users only see actions they can take.

**Code reference:**  
accounts/mixins.py: OwnerOrStaffRequiredMixin
group11_app/views.py: RecordingUpdateView, RecordingDeleteView
group11_app/templates/recordings/recording_detail.html: conditional button display

**Consequences:**  
Citizen scientists can now manage their own recordings while researchers retain the ability to moderate any recording. StaffRequiredMixin remains available for views that require pure researcher-only access. The permission logic is centralised so future views with ownership requirements can reuse the same mixin.