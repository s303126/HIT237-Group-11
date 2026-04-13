### ADR-6: Use fixtures for ThreatStatus and FaunaGroup seeding

**Author:** Melanie Bardoux

**Status:** Accepted 

**AI Usage:**  
AI assistant used to generate fixture content based on provided data. Decision to use fixtures over a management command was made by Melanie Bardoux based on the static, small-scale nature of the data.

**Context:**  
ThreatStatus and FaunaGroup are small, static lookup tables that do not change frequently and do not depend on any external data source. They need to be populated before the Species table can be populated, as Species has foreign keys to both.

**Alternatives considered:**  
- Option 1: Management command - more flexible but unnecessary for small static datasets

- Option 2: Hardcode in views or models - not reusable or portable across environments

**Decision:**  
Use Django fixtures (.json format) stored in group11_app/fixtures/. Fixtures are reuseable, version controlled, and can be loaded into any environment with a single manage.py loaddata command.

**Code reference:**  
group11_app/fixtures/threat_status.json — 13 ThreatStatus records

group11_app/fixtures/fauna_groups.json — 6 FaunaGroup records

**Consequences:**  
Fixtures must be loaded before running the load_species management command, as Species records depend on both ThreatStatus and FaunaGroup existing in the database. 

Load order is: threat_status.json → fauna_groups.json → load_species.
