import csv
from django.core.management.base import BaseCommand
from eloapp.models import Rider

class Command(BaseCommand):
    help = 'Import first 100 riders from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')
        #parser.add_argument('race_name', type=str, help='name_of_the_race')
        #parser.add_argument('race_category', type=str, help='category_of_the_race')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        riders_created = 0
        riders_existing = 0

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                
                self.stdout.write(f"CSV headers: {csv_reader.fieldnames}")
                cpt=0
                for row in csv_reader:
                    
                    # Adjust the field names based on your actual CSV structure
                    rider1, created = Rider.objects.get_or_create(
                        firstname=row['prenom'],
                        lastname=row['nom'],
                        rating=1500-cpt*5,
                        ratingtype="Women"
                        #defaults={?
                            # Add any additional fields from your CSV
                            # 'email': row.get('email'),
                            # 'date_of_birth': row.get('date_of_birth'),
                            # Add more fields as needed
                        #}
                    )
                    cpt+=1
                    if created:
                        riders_created += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Created rider: {rider1.firstname} {rider1.lastname}'
                            )
                        )
                    else:
                        riders_existing += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f'Rider already exists: {rider1.firstname} {rider1.lastname}'
                            )
                        )

                    
                    

            self.stdout.write(
                self.style.SUCCESS(
                    f'Import completed. Created {riders_created} riders. '
                    f'Found {riders_existing} existing riders.'
                )
            )

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'Could not find file: {csv_file_path}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error importing riders: {str(e)}')
            )