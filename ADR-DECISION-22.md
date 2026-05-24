### ADR-22: Custom Exception handlers for capping the submitted audio file length, and preventing anomaly resolution errors due stale pages 

**Date:** 25/05/26

**Author:** Isaac Jessen

**Status:** Accepted

**AI Usage:**  
Framework was coded manually, Claude AI was used to create the validation logic within views.py

**Context:**  
Currently the site allows users to submit a recording of any length, meaning users could submit an mp3 that is hours long, which would both slow the site down and also not provide usable data for the record.
**Alternatives considered:**  

- Option 1: Client-side validation and database constraints only, settle with user seeing a non-clear error message for anomaly resolution errors.


- Option 2: Custom exception Handlers to prevent an mp34 that is longer than a minute, and custom exception handlers provide relevant and clear error messages. 

**Decision:**  
Implemented custom exception handlers that validate audio file length at the service layer and prevent anomalies from being resolved multiple times.

**Code reference:**  
views.py
exceptions.py
service.py

**Consequences:**  Adds complexity to the application layer; requires careful testing of concurrent scenarios; service layer validation adds slight processing overhead
