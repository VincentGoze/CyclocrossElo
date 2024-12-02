import csv
import math
from django.core.management.base import BaseCommand
from django.db import transaction
from eloapp.models import Rider, Race, RaceResult
from datetime import datetime

def calculate_elo_change(rating_a, rating_b, result, k=5):# Calculate new Elo ratings for two riders. rating_a: Current rating of Rider A  rating_b: Current rating of Rider B  result: 1 if Rider A wins, 0 if Rider B wins    k: The K-factor, a constant that controls adjustment speed
    expected_a = 1 / (1 + math.pow(10, (rating_b - rating_a) / 400))
    return  k * (result - expected_a)
    

class Command(BaseCommand):
    help = 'Import race from a CSV file and calculate new rating'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')
        
        



    @transaction.atomic


    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        riders_created = 0
        riders_existing = 0
        resultslist=[]


        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                
                self.stdout.write(f"CSV headers: {csv_reader.fieldnames}")
                
                

                for row in csv_reader:
                    
                    racecategory=row['racecategory']
                    if "Women" in racecategory:
                        ratingtype="Women"
                    elif "Junior" in racecategory:
                        ratingtype="Men Junior"
                    else:
                        ratingtype="Men Elite"

                    # Create or retrieve rider
                    rider1, created = Rider.objects.get_or_create(
                        firstname=row['prenom'],
                        lastname=row['nom'],
                        ratingtype=ratingtype
                    )
                    
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
                    

                    # Get the race and the category
                    racename=row['racename']
                    racedate=row['date']
                    race, created2 = Race.objects.get_or_create(name=racename,date=datetime.strptime(racedate, "%d %B %Y").date())
                    


                    #Create the race result

                    raceres=RaceResult.objects.create(
                        position=row['place'],
                        rider=rider1,
                        race=race,
                        previous_rating=rider1.rating,
                        new_rating=rider1.rating, #new rating will be updated after
                        race_category=racecategory
                    )


                    resultslist.append(raceres)
                    self.stdout.write(
                            self.style.SUCCESS(
                                f'Created result: {raceres.position} {raceres.rider}'
                            )
                        )
                    

                
                #Calculate elo ratings
                bulklist=[]
                n_results=len(resultslist)
                for i in resultslist:
                    rtgchange=0
                    

                    # For smaller races, compare against all other rider
                    if(n_results<32):
                        for j in resultslist:
                            if j!=i:
                                chg=calculate_elo_change(i.previous_rating,j.previous_rating,int(i.position)<int(j.position))
                                rtgchange+=chg
                                self._log_rating_change(i.rider, j.rider, chg)
                    
                    else: #To avoid too much rating changes in races with a lot of riders, we calculate rating changes only for the 3O closest riders in the race. Implemented the 24/11/24
                        comparison_riders = []
                        rider_pos = int(i.position)

                        if rider_pos <= 16:
                            # Front group: compare with first 31 riders
                            comparison_riders = [j for j in resultslist if int(j.position) <= 31 and j != i]
                        elif rider_pos >= n_results - 15:
                            # Back group: compare with last 30 riders
                            comparison_riders = [j for j in resultslist if int(j.position) >= n_results - 30 and j != i]
                        else:
                            # Middle group: compare with 15 riders ahead and behind
                            comparison_riders = [j for j in resultslist if j != i and abs(int(j.position) - rider_pos) <= 15]



                        for j in comparison_riders:
                            chg = calculate_elo_change(
                                i.previous_rating,
                                j.previous_rating,
                                int(i.position) < int(j.position)
                            )
                            rtgchange += chg
                            self._log_rating_change(i.rider, j.rider, chg)
                        
                    self.stdout.write('-----------------------------------------')
                    i.new_rating=round(rtgchange+i.new_rating,1)
                    bulklist.append(i)
                    i.rider.rating=i.new_rating

                #Bulk update    
                RaceResult.objects.bulk_update(bulklist, ['new_rating'])
                Rider.objects.bulk_update([i.rider for i in bulklist], ['rating'])



                #Show ratings change
                for i in resultslist:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Rating change: {i.rider} went from {i.previous_rating} to {i.new_rating}'
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

    def _log_rating_change(self, rider1, rider2, change):
        """Log the rating change between two riders."""
        self.stdout.write(
            self.style.SUCCESS(
                f'Rating change: {rider1} gained {change} points in the duel with {rider2}'
            )
        )