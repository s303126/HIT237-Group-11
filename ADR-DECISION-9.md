### ADR-009: Use base template inheritance and feature-based template organisation

**Author:** Aaron Madelo 

**Status:** Accepted

**AI Usage:**  
AI assistant used for repeatable Django code structures.  

**Context:**  
The application uses multiple pages (home, recordings, species, anomalies) that share common page layout and styling. The pages' layout elements feature header, navigation, footer, and static assets. Repeating the structure 


**Alternatives considered:**
- Option 1: Create standalone templates for each page  
  - Pros: simple to implement initially  
  - Cons: duplicates layout code and reduces maintainability  

- Option 2: Use a shared base template with child templates extending it  
  - Pros: enforces consistency, reduces duplication, supports DRY principle  
  - Cons: requires understanding of Django template inheritance  

**Decision:**  
A shared `base.html` template was created to define global layout and static assets. All other templates extend this base template and define content using Django block tags. Templates are organised into feature-based directories (`recordings/`, `species/`, `anomalies/`) to improve clarity and scalability.

**Code reference:**  
group11_app/templates/base.html  
group11_app/templates/home.html  
group11_app/templates/recordings/  
group11_app/templates/species/  
group11_app/templates/anomalies/

**Consequences:**  
- Ensures consistent layout across all pages  
- Simplifies updates to shared UI components  
- Improves readability and organisation of templates  
- Requires correct block usage to avoid template errors