from django.db import models

# Create your models here.



class Rider(models.Model):
  firstname = models.CharField(max_length=255)
  lastname = models.CharField(max_length=255)
  rating = models.FloatField(default=800)
  ratingtype = models.CharField(max_length=50, default="Men Elite")

  current_position = models.PositiveIntegerField(null=True, blank=True)


  position_change = models.IntegerField(null=True, blank=True)  # Can store negative and positive values


  rating_change = models.FloatField(null=True, blank=True)   


  
  def __str__(self):
    return f"{self.firstname} {self.lastname}"


class Race(models.Model):
    name = models.CharField(max_length=200)
    date = models.DateField()
    category_choices = [
        ('C1', 'UCI C1'),
        ('C2', 'UCI C2'),
        ('NC', 'National Championship'),
        ('CDM', 'Coupe du Monde'),
    ]
    category = models.CharField(max_length=3, choices=category_choices,default="C2")
    
    def __str__(self):
        return f"{self.name}"    

class RaceResult(models.Model):
    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name='results')
    rider = models.ForeignKey(Rider, on_delete=models.CASCADE, related_name='results')
    position = models.PositiveIntegerField()
    previous_rating = models.FloatField()
    new_rating = models.FloatField()
    race_category=models.CharField(max_length=200,default="")
    
    def __str__(self):
        return f"{self.race} - {self.rider} ({self.position})"
    
    class Meta:
        ordering = ['position']
        #unique_together = ['race', 'rider']  # A rider can only have one result

