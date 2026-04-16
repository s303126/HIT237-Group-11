### ADR-9.5: Adjust Views to Utilise Models and Querysets, Create views for full site Functionality

**Author:** Isaac Jessen

**Status:** Accepted | superseeds ADR 6.5

**AI Usage:**  
copilot used to instruct how to copy manually created view with adjustments so that other views can be created in the same method.
copilot used for bugfixing
**Context:**  
The views were class-based but did not utilise the quersyets and methods in place, and instead defined its own seperate functions. Project has progressed and views for full site functionality are possible to be implemented and are required.
**Alternatives considered:**  

- adjust views to use already created models and querysets, create more views (and surround urls etc.) for full site functionality.

- Keep current views and create any new views in the correct method, accept loss of marks


**Decision:**  
Recreate all views to be class based and align with the rubric. Create new views (and urls etc.) for full site functionality, including:
- submitting recordings and all pages surrounding that feature
- submission page to allow the viewing of all recordings
- species page to allow the viewing of all species
- anomaly page to view all recordings flagged as an anomaly 
- flagging recording as anomaly feature and its form page  

**Code reference:**  
views branch: group11_app/views.py 

**Consequences:**  
Views could be created incorrectly and then must be rewritten
