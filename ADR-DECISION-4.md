### ADR-4: Preserve NT-specific threat status codes rather than mapping to base codes

**Author:** Melanie Bardoux

**Status:** Accepted

**AI Usage:**  
Issue identified by Melanie Bardoux while reviewing the spreadsheet data. AI assistant used to discuss options. Decision made by Melanie Bardoux based on the app's purpose of flagging anomalies in NT wildlife recordings.

**Context:**  
The NT Fauna Species Checklist uses compound threat status codes such as EN-EXNT (Endangered, Extinct in the NT) and VU-EXNT (Vulnerable, Extinct in the NT). The initial implementation mapped these down to their base IUCN codes (EN, VU etc.), which removes the NT-specific information. 

**Alternatives considered:**  
- Option 1: Map compound codes to base codes - simple but loses NT-specific context that is directly relevant to anomaly flagging

- Option 2: Add NT-specific fields to ThreatStatus model - more structured but requires making changes to existing models

**Decision:**  
Add five additional ThreatStatus fixture entries for the NT-specific compound codes: CR-PE, EN-EXNT, EN-EWNT, VU-EXNT, and LC-EXNT. Each has a clear label and description explaining the NT context.

The STATUS_MAP in load_species.py was updated to map these codes to their own ThreatStatus records rather than their base codes.

**Code reference:**  
group11_app/fixtures/threat_status.json: entries pk 9–13

group11_app/management/commands/load_species.py: STATUS_MAP


**Consequences:**  
ThreatStatus fixture now contains 13 records instead of 8. Species with NT-specific statuses are correctly identified in the database, supporting more accurate anomaly flagging. No model changes were required.