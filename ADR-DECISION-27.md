### ADR-26: Implemented Pagination to Species, Anomalies, Recordings and their search results

**Date:** 30/05/2026

**Author:** Isaac Jessen

**Status:** Accepted

**AI Usage:**
Claude IA was used to style the bottom navigation bar to match the rest of the website. Claude AI was used to teach me how to add pagination

**Context:**
Currently on the species page, the anomalies page and the recordings page, all items are listed on the one page. this means that when there's many entries, the page becomes extremely long. This is especialy a problem for the species page.

**Alternatives considered:**

- Option 1: Add pagination through a single view and a partial template. Use Django’s built-in Paginator class in each relevant view (Species, Anomalies, Recordings, and search results), and render page controls through a shared reusable partial template (_pagination.html).

- Option 2: Replace pagination with automatic loading of additional results as the user scrolls. This would improve perceived fluidity but requires additional JavaScript/HTMX logic and more complex state handling (especially for search and filtering).

- Option 3: Load all results and handle filtering/display on the frontend. Fetch all records at once and use JavaScript to paginate or filter client-side. This reduces backend complexity but becomes inefficient and slow as dataset size grows, especially for Species.

**Decision:**
Option 1 was selected: implement server-side pagination using Django’s Paginator, with a reusable pagination partial (_pagination.html) shared across Species, Anomalies, Recordings, and search result views.

This approach was chosen due to its simplicity, reliability, and alignment with Django’s standard patterns. It also ensures consistent behavior across pages without requiring additional frontend frameworks or heavy JavaScript.

**Code reference:**
group11_app/templates/partials/_pagination.html:
group11_app/views.py:


**Consequences:**
Requires repeated integration of pagination logic across multiple views.
Slightly increases template complexity due to pagination partial inclusion.
Introduces page reloads when navigating between pages (less smooth than infinite scroll).
