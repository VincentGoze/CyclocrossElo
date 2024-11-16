from django.core.management.base import BaseCommand
from django.db import transaction
from eloapp.models import Rider, Race, RaceResult
from datetime import date, timedelta
from django.utils import timezone



def get_rating_at_date(rider_id, target_date):
    """
    Returns the rating of a rider at a specific date.
    If no race result exists after the target date, the current rating is returned.
    """
    # Get the rider object
    rider = Rider.objects.get(id=rider_id)
    
    # Get the race results after the target date, ordered by race date
    race_results_after_date = rider.results.filter(race__date__gt=target_date).order_by('race__date')
    
    if race_results_after_date.exists():
        # If there are results after the target date, return the new_rating from the oldest result
        first_result_after_date = race_results_after_date.first()  # Get the first (oldest) result after the target date
        return first_result_after_date.previous_rating
    else:
        # If no results exist after the target date, return the current rating
        return rider.rating

class Command(BaseCommand):
    help = 'Calculate position in the ranking and give rating changes and position changes compared to last week'


    @transaction.atomic


    def updateranking(self, typeranking):
    
        # Calculate the date 7 days ago
        seven_days_ago = timezone.now() - timedelta(days=7)

        # Fetch all riders and order them by rating
        riders = Rider.objects.filter(ratingtype=typeranking).order_by('-rating')

        # Calculate the rider's ranking 7 days ago
        # Get the riders' ratings 7 days ago
        riders_seven_days_ago = []
        for rider in riders:
            rating_7_days_ago = get_rating_at_date(rider.id, seven_days_ago.date())  # Use the function we defined earlier
            riders_seven_days_ago.append({
                'rider': rider,
                'rating_7_days_ago': rating_7_days_ago
            })

        # Sort riders by their rating 7 days ago to get their previous positions
        riders_seven_days_ago_sorted = sorted(riders_seven_days_ago, key=lambda x: x['rating_7_days_ago'], reverse=True)

        # Create a dictionary to map riders to their positions 7 days ago
        position_map = {rider_data['rider'].id: (idx + 1, rider_data['rating_7_days_ago']) for idx, rider_data in enumerate(riders_seven_days_ago_sorted)}

        # Now, add the change in positions based on the current rating vs the 7 days ago rating
        ranking_with_changes = []
        for idx, rider in enumerate(riders, start=1):
            # Find the previous position of the rider 7 days ago
            prev_position = position_map.get(rider.id)
        
            # Determine position change (current position - previous position)
            position_change = prev_position[0] - idx
            
            rating_change=round(rider.rating-prev_position[1],1)

            # Add the change information to the rider's data
            rider.current_position=idx
            rider.position_change=position_change
            rider.rating_change=rating_change
        Rider.objects.bulk_update(riders, ['current_position','position_change','rating_change'])

    
        
    def handle(self, *args, **options):  
        for j in ['Men Elite', 'Women', 'Men Junior']:
            self.updateranking(j)



        