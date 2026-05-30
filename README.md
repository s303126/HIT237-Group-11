# Listening to NT's Disappearing Animals

This project is a Django-based web application designed to support biodiversity monitoring in the Northern Territory through acoustic species recordings.

## Project Structure

- `index.html`, `submit.html`, `timeline.html`  
  Initial frontend layout prototypes

- `docs/wireframes/`  
  Basic page layouts demonstrating structure and content placement


## Database Setup

Run the following commands to set up and populate the database.

**1. Run migrations**
```
$ python manage.py migrate
```

**2. Load fixtures**
```
$ python manage.py loaddata group11_app/fixtures/threat_status.json
$ python manage.py loaddata group11_app/fixtures/fauna_groups.json
```

**3. Load species data**
Download the [NT Fauna Species Checklist](https://data.nt.gov.au/dataset/nt-fauna-species-checklist) from data.nt.gov.au and save it to the project root, then run:
```
$ python manage.py load_species --file NT_Species_List_Fauna.xlsx
```

## User Roles and Permissions

The application has three access levels:

**Anonymous (not logged in)**
- View the timeline, species directory and recording details
- Cannot submit recordings or flag anomalies

**Citizen Scientist/Researcher-Pending**
- All anonymous permissions
- Submit recordings (held for review before appearing on the timeline)
- Flag anomalies on recordings
- Edit and delete their own recordings
- Resolve anomalies they have flagged

**Researcher-Approved (requires admin approval)**
- All citizen scientist permissions
- Recordings are auto-approved and appear on the timeline immediately
- Edit and delete any recording
- Approve, reject, restore and delete recordings from the review queue
- Resolve any anomaly
- View users with 3+ flagged or rejected recordings

Users who select researcher at signup are given citizen scientist permissions until approved by an admin through the Django admin panel.

## Test Accounts

| Role | Username | Password
|------|----------|---------|
| Admin | admin | password |
| Citizen Scientist | testuser | Testpass123 |
| Researcher - pending| testresearcher | Testpass123 |
| Researcher - approved| testresearcher2 | Testpass123 |

---
Access the admin panel at `/admin/` with the admin account.

## Notes

These files represent early-stage frontend planning and are not final implementations. They are intended to guide development and support architectural decisions documented in the ADR.