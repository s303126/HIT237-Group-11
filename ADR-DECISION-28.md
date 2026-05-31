### ADR-28: Implemented Service Layer Architecture

**Date:** 31/05/2026

**Author:** Jack Manning

**Status:** Accepted

**AI Usage:**
Claude AI used to assist with the implementation process.

**Context:**
Cross-model operations that involve more than one model in views.py were being handled directly inside view classes and functions. This mixed business logic with request/response handling, making the views harder to read and the logic harder to reuse or test independently.

**Alternatives considered:**
- Keeping all logic in views.py — rejected as it mixes HTTP handling with business logic and makes cross-model operations harder to isolate.
- Moving logic into model methods — rejected as operations involving multiple unrelated models do not belong to any single model.

**Decision:**
Cross-model operations were moved from views.py into dedicated service functions in services.py. This includes recording creation and status changes (Recording + User), anomaly flagging and resolution (Anomaly + Recording + User), and context aggregation for pages that query multiple models together (Recording + Species, Recording + Anomaly). Validation helpers already present in services.py were retained and are now called exclusively from within the service functions rather than directly from views.


**Code reference:**
group11_app/services.py
group11_app/views.py

**Consequences:**
- Views are now only responsible for request handling, permission checks, and rendering.
- Cross-model operations are defined in one place, making them easier to maintain and reuse.
- The validation functions in services.py are no longer imported directly into views.py, as they are encapsulated within the service functions.
- Future features involving the same models can be added to services.py without modifying views.