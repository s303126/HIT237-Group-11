### ADR-009: Develop templates using static placeholder content with planned dynamic integration

**Author:** Aaron Madelo

**Status:** Accepted

**AI Usage:**  
AI assistant used to refine wording and structure of this ADR. Development approach was chosen during frontend implementation.

**Context:**  
Frontend development needed to begin before backend logic (QuerySets, ModelForms, and data retrieval) was complete. Waiting for backend implementation would delay progress and increase integration complexity later in the project.

**Alternatives considered:**
- Option 1: Wait for backend completion before building templates  
  - Pros: templates can be written directly using real data  
  - Cons: delays frontend development and increases dependency on backend progress  

- Option 2: Build templates with static placeholder content and annotate future dynamic replacements  
  - Pros: allows immediate frontend progress, supports layout testing, and clarifies expected data structures  
  - Cons: requires later replacement of placeholder content and careful handling of template syntax  

**Decision:**  
Templates were developed using static placeholder data to define layout and user interface behaviour. Future dynamic functionality was documented using Django-compatible comments and planned context variables, allowing seamless transition to backend integration.

**Code reference:**  
group11_app/templates/base.html
group11_app/templates/home.html  
group11_app/templates/recordings/recording_list.html  
group11_app/templates/recordings/recording_detail.html  
group11_app/templates/recordings/species_detail.html
group11_app/templates/species/species_list.html  
group11_app/templates/anomalies/anomaly_form.html  
group11_app/templates/anomalies/anomaly_list.html

**Consequences:**  
- Enables frontend and backend development to proceed in parallel  
- Improves clarity of expected data structures for integration  
- Allows early UI testing within Django  
- Requires later replacement of static content with dynamic data  
- Highlighted the need to avoid duplicate Django template blocks in commented code to prevent rendering errors