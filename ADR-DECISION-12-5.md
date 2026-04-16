### ADR-12.5: Merge view testing branch to main branch

**Author:** Isaac Jessen

**Status:** Accepted

**AI Usage:**  
none.
**Context:**  
The view branch has been approved by team members and is ready to be merged into main.
**Alternatives considered:**  

- merge via direct merge

- merge specific code lines into main branch 


**Decision:**  
Merge full files directly into main. I had tried merging specific code lines but it broke the code and so I reversed the merge.
**Code reference:**  
Main branch:

**Consequences:**  
merge could delete or unintentionally edit files in main branch