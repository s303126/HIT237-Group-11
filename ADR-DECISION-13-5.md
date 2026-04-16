### ADR-13.5: implemented functional audio player

**Author:** Isaac Jessen

**Status:** Accepted

**AI Usage:**  
copilot used to ask for instructions on the process of isntalling mp3 playing functionality in a django site.
**Context:**  
the .mp3 files are accepted in the submission form, but so are all other file types, and .mp3 files do not play in the recording details section
**Alternatives considered:**  

- adjust current views and models, urlpattern and settings to accept audio

- Create a new view method (e.g., audio_player_view) that specifically handles .mp3 playing.


**Decision:**  
adjust current views and models, urlpattern and settings to accept audio files only and to properly play them back in the recording details page.
**Code reference:**  
views branch: group11_app/views.py 

**Consequences:**  
Views could be created incorrectly and then must be rewritten
