import csv
from django.core.management.base import BaseCommand
from eloapp.models import Rider, Race, RaceResult


def calculate_elo_change(rating_a, rating_b, result, k=5):# Calculate new Elo ratings for two riders. rating_a: Current rating of Rider A  rating_b: Current rating of Rider B  result: 1 if Rider A wins, 0 if Rider B wins    k: The K-factor, a constant that controls adjustment speed
    expected_a = 1 / (1 + math.pow(10, (rating_b - rating_a) / 400))
    return  k * (result - expected_a)
    

class Command(BaseCommand):
    def handle(self, *args, **options):
        riders = Rider.objects.filter(ratingtype="Men Elite").order_by('-rating')[:12]
        with open('viz1.csv', 'w', newline='',encoding='utf-8') as file:
            writer = csv.writer(file)
            field = ["Name","Rating","Change","Position","PositionChange"]
            writer.writerow(field)

            for j in riders:
                writer.writerow([j,j.rating,j.rating_change,j.current_position,j.position_change])
        riders = Rider.objects.filter(ratingtype="Women").order_by('-rating')[:12]
        with open('viz2.csv', 'w', newline='',encoding='utf-8') as file:
            writer = csv.writer(file)
            field = ["Name","Rating","Change","Position","PositionChange"]
            writer.writerow(field)

            for j in riders:
                writer.writerow([j,j.rating,j.rating_change,j.current_position,j.position_change])
