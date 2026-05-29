### ADR-24: Session-based authentication over token-based authentication

**Date:** 29/05/2026

**Author:** Melanie Bardoux

**Status:** Accepted

**AI Usage:**
Nil

**Context:**
The application requires an authentication mechanism to manage user sessions across page requests. Two common approaches are session-based and token-based authentication.

**Alternatives considered:**

- Option 1: Session-based authentication. Django stores session data on the server and identifies users via a browser cookie. Built into Django with no additional setup. Includes CSRF protection by default.

- Option 2: Token-based authentication. The server issues a token that the user sends with each request. Better suited for APIs and mobile apps but requires additional libraries and manual CSRF handling.

**Decision:**
Use Django's built-in session-based authentication. The application is a browser-based web app using form submissions, so session authentication is the appropriate choice. CSRF protection is included by default through Django's middleware and template tags

**Code reference:**
group11_project/settings.py: SessionMiddleware, CsrfViewMiddleware
accounts/views.py: LoginView, LogoutView

**Consequences:**
Authentication is handled entirely by Django's built-in framework with no additional dependencies. If the application later needs to support a mobile app or API, token-based authentication may be more appropriate.
