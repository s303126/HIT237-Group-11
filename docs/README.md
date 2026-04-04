# Listening to NT's Disappearing Animals

This project is a Django-based web application designed to support biodiversity monitoring in the Northern Territory through acoustic species recordings.

## Project Structure

- `index.html`, `submit.html`, `timeline.html`  
  Initial frontend layout prototypes

- `flowchart.md`  
  Contains basic flowchart for the website

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

## Notes

These files represent early-stage frontend planning and are not final implementations. They are intended to guide development and support architectural decisions documented in the ADR.