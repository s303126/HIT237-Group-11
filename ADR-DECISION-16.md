### ADR-16: Extend UserCreationForm for user registration with role selection

**Date:** 21/05/2026

**Author:** Melanie Bardoux

**Status:** Accepted

**AI Usage:**   
Claude AI used to assist writing the initial form structure. Fields and integration with the custom User model reviewed and adapted by Melanie Bardoux."

**Context:**  
The site requires optional user registration functionality where users can create accounts and select their role (researcher or citizen_scientist). The registration form must collect username, password, email, first name, last name, and role while ensuring password validation and security.

**Alternatives considered:**  

- Option 1:  Extend UserCreationForm. Built-in password validation and security are inherited without additional implementation. Requires only adding the extra fields needed for the custom User model.

- Option 2: Build a custom ModelForm from scratch. Full control over validation logic, but password confirmation and strength validation would need to be reimplemented manually.

**Decision:**  
Extend UserCreationForm and add the additional fields required by the custom User model. Password validation and confirmation are handled without requiring custom implementation.

**Code reference:**  
accounts/forms.py: CustomUserCreationForm class extending UserCreationForm
accounts/views.py: SignupView using CustomUserCreationForm
accounts/templates/accounts/signup.html

**Consequences:**  
Password validation and confirmation are handled by Django core. Role selection at registration allows users to self-identify their account type on signup. Future consideration: a researcher role verification process will be required to prevent unauthorised researcher access.