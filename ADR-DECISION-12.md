### ADR-12: Retain Unused QuerySets for potential use in Assessment 4

**Author:** Melanie Bardoux

**Status:** Accepted

**AI Usage:**  None

**Context:**  
Several custom QuerySets defined in the model managers are not currently referenced in Views. A decision was required on whether to remove unused QuerySets to keep the codebase lean or retain them for future use.

**Alternatives considered:**  

- Remove unused QuerySets: Keeps the codebase lean but loses functionality that directly supports Assessment 4 requirements such as authentication, user management, and advanced filtering.

- Retain unused QuerySets: Adds unreferenced code to codebase but preserves pre-tested functionality for potential use in Assessment 4.

**Decision:**  
Unused QuerySets were retained. The custom managers were designed to support the full feature set of the site, not only the features implemented in Assessment 2. Many of the unused QuerySets are directly applicable to Assessment 4 requirements including user authentication, service layer implementation, and advanced data filtering.

**Code reference:**  
group11_app/models.py — FaunaGroupManager, SpeciesManager, RecordingManager, AnomalyManager

**Consequences:**  
The codebase contains QuerySets not yet referenced by any view. The retention reflects intentional, pre-emptive design decisions rather than dead code, and will be utilised as the site is extended in Assessment 4.