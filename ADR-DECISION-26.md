### ADR-26: Added search bar to species, anomalies and records lists

**Date:** 30/05/2026

**Author:** Isaac Jessen

**Status:** Accepted

**AI Usage:**
Implemented the code from the below youtube tutorial manually, and Used Claude to edit it to fit within our project. This included editing the code so that the singular search view worked for all 3 pages the search bar is accesible on. 
https://www.youtube.com/watch?v=_F46VGtidIQ
ChatGPT used to help create ADR
**Context:**
Currently there are thousands of species in the species page but no way to filter or search for any. If the website gains popularity and usage, the anomalies and recordings page will suffer the same issue.

**Alternatives considered:**

- Option 1: A single shared search view in Django that routes queries based on a type parameter (species, anomalies, recordings). Each model defines its own search(query) method using Django ORM filters. Results are rendered using shared partial templates for each result type.

- Option 2: Implement a dedicated search function for each page (Species, Anomalies, Recordings), each with its own view and logic. This would be straightforward but would duplicate logic across multiple views and templates, making maintenance harder.

**Decision:**
A shared search system was implemented using a single Django search view that handles multiple content types (species, recordings, and anomalies) through a type query parameter.
Each model implements a dedicated search(query) method encapsulating its own filtering logic using Django ORM Q objects. This keeps search logic modular while still allowing a single entry point for all search functionality.

**Code reference:**
group11_app/models.py
group11_app/templates/anomalies/anomaly_list.html
group11_app/templates/search.html
group11_app/templates/search_partials/_anomaly_results.html
group11_app/templates/search_partials/_recording_results.html
group11_app/templates/search_partials/_species_results.html
group11_app/templates/species/species_list.html
group11_app/urls.py
group11_app/views.py

**Consequences:**
Slight increase in complexity within the search() view due to routing logic.
Requires maintaining consistency across multiple search() implementations in models.
Still relies on full-page reloads (no instant filtering like client-side search).