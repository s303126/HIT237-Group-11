### ADR-13: Implement Custom ModelAdmin for All Models

**Author:** Melanie Bardoux

**Status:** Accepted | (Supersedes ADR-11)

**AI Usage:**  
Claude.ai assistance with drafting initial AnomalyAdmin configuration 

**Context:**  
ADR-11 registered all models using basic registration with a custom AnomalyAdmin only. Following the rationale established in ADR-12 (that pre-built functionality identified as relevant to Assessment 4 requirements should be retained), the admin interface was reconsidered to reflect the full data model, adding functionality to Assessment 2 while preparing for Assessment 4

**Alternatives considered:**  

- Retain basic registration for all models except Anomaly: Functional but provides limited admin usability and does not expose model fields that will be relevant in Assessment 4.

- Custom ModelAdmin for all models: More comprehensive, exposes all relevant fields, supports filtering and search, and prepares the admin interface for Assessment 4 features.


**Decision:**  
Custom ModelAdmin was implemented for all models. Each ModelAdmin is configured with list_display, list_filter where appropriate, and search_fields to support data management. This decision aligns with the design rationale established in ADR-12.

**Code reference:**  
group11_app/admin.py

**Consequences:**  
All models are visible and manageable through the Django admin interface with purposeful field display and filtering. Fields not yet active in Views are available in admin in preparation for Assessment 4 implementation.