### ADR-5: Use management command for Species data seeding

**Author:** Melanie Bardoux

**Status:** Accepted

**AI Usage:**  
AI assistant used to write the initial management command. Column mapping, data cleaning decisions and NT-specific status handling reviewed, edited and adapted by Melanie Bardoux after inspecting the spreadsheet structure directly.

**Context:**  
The Species table requires importing 2515 records from the NT Fauna Species Checklist (data.nt.gov.au), an external XLSX file with one sheet per fauna group. 

The data required mapping to the project's model fields, including handling missing common names, threat status codes, and introduced/native status.


**Alternatives considered:**  
- Option 1: Fixture - impractical for 2515 records requiring transformation from an external source

- Option 2: Manual data entry - not feasible at this scale

**Decision:**  
Write a custom management command (load_species.py) using pandas and openpyxl to read the NT Fauna Species Checklist. 

The command maps each sheet to a FaunaGroup, maps the TERRITORY PARKS AND WILDLIFE ACT CLASSIFICATION column to ThreatStatus, and derives is_native and is_introduced from the INTRODUCED STATUS column. Species with no common name fall back to the scientific name rather than being skipped.

**Data source:** NT Fauna Species Checklist, Northern Territory Government, data.nt.gov.au.

**Code reference:**  
group11_app/management/commands/load_species.py

**Consequences:**  
pandas and openpyxl are required dependencies and have been added to requirements.txt.

 The NT Fauna Species Checklist XLSX file is excluded from the repository via .gitignore and must be downloaded separately before running the command. 

The command is safe to re-run as update_or_create prevents duplicate records.