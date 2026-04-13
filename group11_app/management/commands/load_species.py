import os
import pandas as pd
from django.core.management.base import BaseCommand
from group11_app.models import Species, FaunaGroup, ThreatStatus


class Command(BaseCommand):
    help = 'Populates the database with NT fauna species data from the NT Species List Fauna spreadsheet'

    # Connects spreadsheet names to FaunaGroup names
    SHEET_TO_GROUP = {
        'FROGS': 'Frogs',
        'BIRDS': 'Birds',
        'MAMMALS': 'Mammals',
        'REPTILES': 'Reptiles',
        'FISH': 'Fish',
        'INVERTEBRATES': 'Invertebrates',
    }

    # Connects NT status codes to standard ThreatStatus codes
    # Some codes have suffixes like -EXNT (extinct in NT) or -EWNT (extinct in wild in NT)
    #these are mapped to their base code
    STATUS_MAP = {
        'EX': 'EX',
        'EW': 'EW',
        'CR': 'CR',
        'CR-PE': 'CR-PE',
        'EN': 'EN',
        'EN-EXNT': 'EN-EXNT',
        'EN-EWNT': 'EN-EWNT',
        'VU': 'VU',
        'VU-EXNT': 'VU-EXNT',
        'NT': 'NT',
        'LC': 'LC',
        'LC-EXNT': 'LC-EXNT',
        'DD': 'DD',
        'NE': None,      # Not Evaluated — no threat status assigned
        '(Int)': None,   # Introduced — no threat status assigned
        '(NL)': None,    # Not Listed — no threat status assigned
    }

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='NT_Species_List_Fauna.xlsx',
            help='Path to the NT Species List Fauna XLSX file'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing species before seeding'
        )

    def handle(self, *args, **options):
        filepath = options['file']

        if not os.path.exists(filepath):
            self.stderr.write(self.style.ERROR(f'File not found: {filepath}'))
            self.stderr.write('Please provide the path to the NT Species List Fauna XLSX file.')
            self.stderr.write('Example: python manage.py seed_species --file path/to/NT_Species_List_Fauna.xlsx')
            return

        if options['clear']:
            self.stdout.write('Clearing existing species...')
            Species.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing species cleared.'))

        created_count = 0
        skipped_count = 0
        error_count = 0

        for sheet_name, group_name in self.SHEET_TO_GROUP.items():
            self.stdout.write(f'Processing {sheet_name}...')

            try:
                df = pd.read_excel(filepath, sheet_name=sheet_name, header=4)
                # Fix 3 — slice to first 10 columns to avoid 11th None column mismatch
                df = df.iloc[:, :10]
                df.columns = [
                    'CLASS', 'ORDER', 'FAMILY', 'GENUS', 'SPECIES',
                    'SUBSPECIES', 'COMMON_NAME', 'NT_STATUS', 'EPBC_STATUS', 'INTRODUCED_STATUS'
                ]

                fauna_group, _ = FaunaGroup.objects.get_or_create(
                    name=group_name,
                    defaults={'icon': ''}
                )

                for _, row in df.iterrows():
                    try:
                        common_name = str(row['COMMON_NAME']).strip() if pd.notna(row['COMMON_NAME']) else ''
                        # Fix 1 — SPECIES column already contains the full scientific name
                        scientific_name = str(row['SPECIES']).strip() if pd.notna(row['SPECIES']) else ''
                        nt_status_raw = str(row['NT_STATUS']).strip() if pd.notna(row['NT_STATUS']) else ''
                        introduced_status = str(row['INTRODUCED_STATUS']).strip() if pd.notna(row['INTRODUCED_STATUS']) else ''

                        # Skip rows with missing scientific name
                        if not scientific_name or scientific_name == ' ':
                            skipped_count += 1
                            continue

                        # Fix 2 — fall back to scientific name if common name is missing
                        if not common_name:
                            common_name = scientific_name

                        # Determine threat status
                        threat_status = None
                        if nt_status_raw in self.STATUS_MAP:
                            mapped_code = self.STATUS_MAP[nt_status_raw]
                            if mapped_code:
                                threat_status = ThreatStatus.objects.filter(code=mapped_code).first()

                        # Determine native/introduced status
                        is_native = introduced_status in ['Native to the N.T.', 'Endemic to the N.T.']
                        is_introduced = introduced_status == 'Introduced'

                        # Create or update species
                        species, created = Species.objects.update_or_create(
                            scientific_name=scientific_name,
                            defaults={
                                'common_name': common_name,
                                'fauna_group': fauna_group,
                                'threat_status': threat_status,
                                'is_native': is_native,
                                'is_introduced': is_introduced,
                                'description': '',
                            }
                        )

                        if created:
                            created_count += 1
                        else:
                            skipped_count += 1

                    except Exception as e:
                        error_count += 1
                        self.stderr.write(f'Error processing row: {e}')

            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Error processing sheet {sheet_name}: {e}'))

        self.stdout.write(self.style.SUCCESS(
            f'\nSeeding complete!'
            f'\n  Created: {created_count} species'
            f'\n  Updated/skipped: {skipped_count} species'
            f'\n  Errors: {error_count}'
        ))
