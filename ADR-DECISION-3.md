### ADR-3: Remove is_anomaly field from Recording model

**Author:** Melanie Bardoux

**Status:** Accepted

**AI Usage:**  
Redundancy identified by Melanie Bardoux while reviewing models in preparation for writing QuerySet managers. AI assistant used to help explore alternatives and consequences.

**Context:**
The Recording model contains both an is_anomaly boolean field and a separate Anomaly model. The Anomaly model already captures whether a recording has been flagged, by which user, why, and whether it has been resolved. This results in the is_anomaly field on Recording to be redundant, contradicting DRY philosophy, and creates a risk of the two becoming out of sync.

**Alternatives considered:**
- Option 1: Keep both - simple to check is_anomaly directly but risks the two getting out of sync if one is updated without the other

- Option 2: Remove is_anomaly and use Anomaly model only - single source, no redundancy, cleaner design but views and templates may require updating.

**Decision:**  
Proposed to remove is_anomaly and anomaly_flag_reason from Recording and rely solely on the Anomaly model. Whether a recording has been flagged can be determined by checking recording.anomaly_set.exists(). Pending group approval.

**Code reference:**  
group11_app/models.py — Recording model (is_anomaly field, anomaly_flag_reason field, flag() method, unflag() method)

**Consequences:**  
Any views or templates checking is_anomaly directly will need to be updated to query the Anomaly model instead. The flag() and unflag() methods on Recording will also need to be removed. The get_flagged() classmethod on Recording will be removed. This simplifies the model and eliminates the risk of data inconsistency.