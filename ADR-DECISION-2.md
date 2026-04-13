### ADR-2: Convert existing classmethods to custom managers

**Author:** Melanie Bardoux

**Status:**  Accepted

**AI Usage:**  
AI assistant used to scaffold initial manager methods. Structure, method selection and justification reviewed, edited and adapted by Melanie Bardoux.

**Context:**  
Initial models used @classmethod to encapsulate query logic directly in the model classes. While functional, classmethods cannot be chained with other QuerySet operations. 

**Alternatives considered:**
- Option 1: Keep @classmethod - already written, familiar syntax, works for simple queries but not chainable and not Django idiomatic
- Option 2: Use a seperate queries.py file - separates query logic from models and keeps views skinny, but is not beneficial for a project of this size where query logic is best kept with models

**Decision:**    
Keep query logic in models.py, aligning with fat models/skinny views. Convert classmethods to custom managers where appropriate. This supports chaining and follows Django conventions for encapsulating query logic while ensuring that query logic is only defined once and reusable anywhere in the codebase.

Not all classmethods were removed. Recording.get_flagged() was left in place as it references is_anomaly, which is pending group discussion about removal (ADR-DECISION-3). 

ThreatStatus.get_threatened() was left as ThreatStatus is a simple lookup table that does not warrant a custom manager. 

Instance methods were not removed or amended as they operate on single objects and serve a different purpose to manager methods.

**Code reference:**  
group11_app/models.py — RecordingManager, AnomalyManager, SpeciesManager, FaunaGroupManager

**Consequences:**  
Recording.get_timeline() replaced by RecordingManager.get_timeline() 

Anomaly.get_unresolved() replaced by AnomalyManager.get_unresolved() 

Anomaly.get_for_species() replaced by AnomalyManager.get_for_species()

Classmethods listed above have been removed and replaced with custom manager methods. Any views calling classmethods directly need to be updated to use Model.objects.method() syntax instead. 

The N+1 query problem is addressed through consistent use of select_related and prefetch_related throughout the managers.