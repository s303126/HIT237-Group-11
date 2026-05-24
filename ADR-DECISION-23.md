### ADR-23: Added custom 404 page

**Date:** 25/05/26

**Author:** Isaac Jessen

**Status:** Accepted

**AI Usage:**  
Ai used to style the 404 page to mimic Aarons site design

**Context:**  
The site functioned with just the inbuilt unstylised 404 page which is very jarring for the user, and does not provide a way for them to return to the homepage. 
**Alternatives considered:**  

- Option 1: Use Django's default built-in 404 error page.

- Option 2: Create a custom stylised 404 page with a link to return to homepage.

**Decision:**  

Implemented a custom 404 error page that matches Aaron's site design and branding. This provides users with a smoother error experience and includes a link to return to the homepage. The custom page is served by configuring Django's error handler in `urls.py` and setting `DEBUG = False` in production to enable custom error page rendering.


**Code reference:**  
settings.py
urls.py
404.html

**Consequences:**  Debug had to be set to False, and allowed hosts set to all/"*". 
