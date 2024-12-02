import csv
from django.core.management.base import BaseCommand
from eloapp.models import Rider, Race, RaceResult
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd




# Create labels with position change symbols
def get_position_change_symbol(change):
    if change > 0:
        return f"▲{change}"  # Up triangle with number
    elif change < 0:
        return f"▼{abs(change)}"  # Down triangle with number
    else:
        return "="  # No change








# def calculate_elo_change(rating_a, rating_b, result, k=5):# Calculate new Elo ratings for two riders. rating_a: Current rating of Rider A  rating_b: Current rating of Rider B  result: 1 if Rider A wins, 0 if Rider B wins    k: The K-factor, a constant that controls adjustment speed
#     expected_a = 1 / (1 + math.pow(10, (rating_b - rating_a) / 400))
#     return  k * (result - expected_a)
    

class Command(BaseCommand):
    def handle(self, *args, **options):
        riders = Rider.objects.filter(ratingtype="Men Elite").order_by('-rating')[:10]
        with open('viz1.csv', 'w', newline='',encoding='utf-8') as file:
            writer = csv.writer(file)
            field = ["Name","Rating","Change","Position","PositionChange"]
            writer.writerow(field)

            for j in riders:
                writer.writerow([j,j.rating,j.rating_change,j.current_position,j.position_change])

        self.createviz(1)


        riders = Rider.objects.filter(ratingtype="Women").order_by('-rating')[:10]
        with open('viz2.csv', 'w', newline='',encoding='utf-8') as file:
            writer = csv.writer(file)
            field = ["Name","Rating","Change","Position","PositionChange"]
            writer.writerow(field)

            for j in riders:
                writer.writerow([j,j.rating,j.rating_change,j.current_position,j.position_change])
        self.createviz(2)


        riders = Rider.objects.filter(ratingtype="Men Junior").order_by('-rating')[:10]
        with open('viz3.csv', 'w', newline='',encoding='utf-8') as file:
            writer = csv.writer(file)
            field = ["Name","Rating","Change","Position","PositionChange"]
            writer.writerow(field)

            for j in riders:
                writer.writerow([j,j.rating,j.rating_change,j.current_position,j.position_change])

        self.createviz(3)        

    def createviz(self,n):
        # Sample data
        data = pd.read_csv(f'viz{n}.csv')

        # Apply the symbols for each row
        data['PositionChangeSymbol'] = data['PositionChange'].apply(get_position_change_symbol)

        # Combine label text
        data['Label'] = data.apply(
            lambda x: f"{x.name + 1} - {x['Name']} ({x['PositionChangeSymbol']})", 
            axis=1
        )

        # Set up the seaborn plot
        sns.set_style("white")
        fig, ax = plt.subplots(figsize=(12, 6.75))

        # Option 3: Inside bars
        sns.barplot(data=data, x='Rating', y='Label', color='#4e79a7', orient='h', ax=ax)
        # for i, (rating, change) in enumerate(zip(data['Rating'], data['Change'])):
        #     ax.text(rating/2, i, f'{rating} ({change:+.1f})', 
        #              ha='center', va='center', color='white', fontweight='bold')
        
        # Add title and labels
        ax.set_xlabel("Points")
        ax.set_ylabel("")
        ax.set_title("Elo Ranking Men Elite")


        plt.tight_layout()

        # Save the plot as a png
        plt.savefig(f"eloapp/static/viz{n}.png", format="png", dpi=150)

