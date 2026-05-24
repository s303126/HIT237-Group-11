### ADR-21: Custom Exception handlers for preventing duplicate submitted records and anomalies

**Date:** 25/05/26

**Author:** Isaac Jessen

**Status:** Accepted

**AI Usage:**  
Framework was coded manually, Claude AI was used to create the validation logic within views.py
AI used to assist in creating ADR

**Context:**  
The site currently allows for a user to submit a recording multiple times and flag a recording as an anomaly for the same reason multiple times.

**Alternatives considered:**  

- Option 1: Client-side validation only (disable submit buttons after initial submission, JavaScript-based form validation)

- Option 2: custom exception handlers to prevent duplicate records and anomalies being submitted.

**Decision:**  
implemented custom exception handlers in `exceptions.py` with validation logic in `views.py` to catch duplicate submission attempts before they reach the database.


**Code reference:**  
views.py
exceptions.py
service.py

**Consequences:**  Adds complexity to the application layer; requires maintenance of custom validation logic; must be tested thoroughly to ensure no edge cases allow duplicates through
