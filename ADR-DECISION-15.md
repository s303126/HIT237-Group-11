### ADR-15: Use Django's built-in LoginView and LogoutView for authentication

**Date:** 21/05/2026

**Author:** Melanie Bardoux

**Status:** Accepted

**AI Usage:**  
Claude AI used to identify Django's built-in authentication views and assist with implementation. Decision rationale and alternatives analysis by Melanie Bardoux.

**Context:**  
Assessment 4 requires implementing user authentication. The application requires secure login/logout functionality and restricted access based on user roles.


**Alternatives considered:**  

- Option 1: Use Django's built-in LoginView and LogoutView. Proven security, maintained by Django core, minimal code required, and integrates directly with Django's authentication system. Less customisation control compared to building from scratch.

- Option 2:  Build custom class-based views. Full control over the authentication flow, but requires manually implementing password hashing, session management, and security measures. Higher risk of introducing vulnerabilities and significantly more development time for functionality Django already provides.

**Decision:**  
Use Django's built-in LoginView and LogoutView with custom templates. Security, session management, and password validation are handled by Django core. Custom templates extend base.html to maintain design consistency.

**Code reference:**  
accounts/urls.py: LoginView and LogoutView 
accounts/templates/accounts/login.html
group11_project/settings.py: LOGIN_URL, LOGIN_REDIRECT_URL, LOGOUT_REDIRECT_URL

**Consequences:**  
Authentication implementation is simplified and security is strengthened through use of Django's core authentication system. Custom templates provide design consistency while built-in views handle authentication logic. 