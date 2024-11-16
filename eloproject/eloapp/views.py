from django.shortcuts import render
from django.http import HttpResponse
from .models import Rider, Race, RaceResult
from django.db.models import Count, Q, Case, When, IntegerField
from django.template import loader
from datetime import date




#some functions to process the views


category_order = Case(
    When(race_category="Men Elite", then=0),  
    When(race_category="Women Elite", then=1),
    When(race_category="Men U23", then=2),
    When(race_category="Women U23", then=3),
    When(race_category="Men Junior", then=4),   
    When(race_category="Women Junior", then=5),   
    default=6,  # Assign lowest priority to other categories
    output_field=IntegerField(), 
)    


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






# Create your views here.




def ranking(request,typeranking,wj=0,u23=0):

    # Fetch all riders and order them by rating
    riders = Rider.objects.filter(ratingtype=typeranking).order_by('-rating')
    if wj:
    	riders=riders.filter(results__race_category="Women Junior").distinct()
    if u23:
    	riders=riders.filter(results__race_category=typeranking.split(' ')[0]+" U23").distinct()
    rider_data=[]
    for rider in riders:
    	position_change_str="=" if rider.position_change ==0 else f"{(rider.position_change):+d}"
    	rating_change_str=f"{rider.rating_change:+.1f}"
    	rider_data.append({'rider':rider, 'position_change_str':position_change_str,'rating_change_str':rating_change_str})

    

    # Pass the updated ranking data to the template
    template = loader.get_template('ranking.html')
    context = {
        'rider_data': rider_data,
    }
    return HttpResponse(template.render(context, request))



def rankingme(request):
	return ranking(request,"Men Elite")

def rankingwe(request):
	return ranking(request,"Women")

def rankingmj(request):
	return ranking(request,"Men Junior")

def rankingwj(request):
	return ranking(request,"Women",1)	

def rankingmu(request):
	return ranking(request,"Men Elite",0,1)

def rankingwu(request):
	return ranking(request,"Women",0,1)




def listofraces(request):
    allraces = Race.objects.all().values().order_by('-date')
    template = loader.get_template('all_races.html')
    context = {
        'allraces': allraces,
    }
    return HttpResponse(template.render(context, request))	


def all_riders(request):
	query = request.GET.get('q')  # Get the search term from the query parameters
	if query:
		filteredriders = Rider.objects.filter(
            Q(firstname__icontains=query) | Q(lastname__icontains=query)
        )
	else:
		filteredriders = Rider.objects.all()  

	allriders = filteredriders.annotate(
	first_place_count=Count('results', filter=Q(results__position=1)),podium_count=Count('results', filter=Q(results__position__lt=4))       #see related_name=results in RaceResult model
	).order_by('-first_place_count','-podium_count')
	template = loader.get_template('all_riders.html')
	context = {
	    'allriders': allriders,
	    }
	return HttpResponse(template.render(context, request))  

def main(request):
    recentraces = Race.objects.order_by('-date')[:5]
    podiums=[RaceResult.objects.filter(race=currace,position__lt=4).annotate(category_order=category_order).order_by('category_order','position') for currace in recentraces]

    context = {
        'raceandpodiums': zip(recentraces,podiums),
    }
    template = loader.get_template('main.html')
    return HttpResponse(template.render(context,request)) 	

def racedetails(request,id):
    template = loader.get_template('racedetails.html')
    race=Race.objects.get(id=id)
    race_results = RaceResult.objects.filter(race=race).annotate(category_order=category_order).order_by('category_order','position')
    for res in race_results:
        # Calculate the difference and add it as an attribute
        res.rating_difference = round(res.new_rating - res.previous_rating,1) if res.new_rating and res.previous_rating else None
    context = {
        'race': race,
        'race_results':race_results
    }
    return HttpResponse(template.render(context, request))    

def riderdetails(request, id):
	mymember = Rider.objects.get(id=id)
	rider_results=RaceResult.objects.filter(rider=mymember).annotate(category_order=category_order).order_by('-race__date')
	for res in rider_results:
        # Calculate the difference and add it as an attribute
		res.rating_difference = round(res.new_rating - res.previous_rating,1) if res.new_rating and res.previous_rating else None
    
	template = loader.get_template('riderdetails.html')
	context = {
    		'mymember': mymember,
    		'rider_results':rider_results
	}
	return HttpResponse(template.render(context, request))  


def change(request):
	data=[]
	for j in ['Men Elite','Women','Men Junior']:
		riders = Rider.objects.filter(ratingtype=j).order_by('-rating_change')[:20]
		data.append(enumerate(riders,1))
	for j in ['Men Elite','Women','Men Junior']:
		riders = Rider.objects.filter(ratingtype=j).order_by('rating_change')[:20]
		data.append(enumerate(riders,1))
	context={'data':data}	
	template = loader.get_template('change.html')
	return HttpResponse(template.render(context, request)) 	


