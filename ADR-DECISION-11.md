### ADR-11: Register All Models in Django Admin with Custom AnomalyAdmin

**Author:** Melanie Bardoux

**Status:** Accepted

**AI Usage:**   
Claude.ai assistance with drafting the custom AnomalyAdmin configuration

**Context:**  
No models were registered in the Django admin panel, therefore unable to view or manage data through the admin interface. As anomaly flagging is a core feature of the site, admin visibility was necessary for testing and management purposes.

**Alternatives considered:**  

- Basic registration for all models: Simple to implement, provides admin visibility but no filtering, search, or practical field display for any model.

- Custom ModelAdmin for all models: More comprehensive but unnecessary at this stage given not all model fields are in active use yet.


**Decision:**  
All models were registered using basic registration to provide immediate admin visibility. A custom AnomalyAdmin was implemented for the Anomaly model as anomaly flagging is a core feature required for testing and management capability, with filtering by resolved status and reason, and search by species and flagging user.

**Code reference:**  
group11_app/admin.py

**Consequences:**  
All models became visible in the Django admin panel. Basic registration for most models provides functional usability.