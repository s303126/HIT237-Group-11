### ADR-XXX: [Initial URL routing and stub view structure for frontend integration]

**Author:** Aaron Madelo 

**Status:** Accepted 

**AI Usage:** AI usage used to assist in structuring of URL routing.

**Context:**
Frotend templates in Django need to be rendered for testing of navigation and layout. Backend logic, 
QuerySets and forms are not yet implemented, but templates require integration with Django's routing system.

**Alternatives considered:**
- Option 1: Delay routing and view creation until backend implementation is completed. 
   - Pro(s): Avoids temporary or placeholder code. 
   - Con(s): Prevents template testing and delays frontend progress.
- Option 2: Create named routes and stub views for early template viewing.
   - Pro(s): Enables early testing; supports validation of navigation; allows parallel development
   - Con(s): Introduces temporary views that require later modification 

**Decision:**
Named routes were defined in 'urls.py', and corresponding stub views were created in 'views.py'. 

**Code reference:**
group11_app/urls.py
group11_app/views.py

**Consequences:**
- Templates can be tested through Django instead of static preview
- Navigation requires Django URL names instead of hardcoded paths
- Stub views require replacement or extension during integration of backend
- Enables parallel development across frontend and backend roles

---

