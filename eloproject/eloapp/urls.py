from django.urls import path
from . import views

urlpatterns = [
    path('main/', views.main, name='main'),
    path('', views.main, name='main'),
    path('ranking/', views.rankingme, name='ranking'),
    path('ranking2/', views.rankingwe, name='ranking2'),
    path('ranking3/', views.rankingmj, name='ranking3'),
    path('ranking4/', views.rankingwj, name='ranking4'),
    path('ranking5/', views.rankingmu, name='ranking5'),
    path('ranking6/', views.rankingwu, name='ranking6'),
    path('races/', views.listofraces, name='all_races'),
    path('riders/', views.all_riders, name='all_riders'),
    path('riders/<int:id>', views.riderdetails, name='details'),
    path('races/<int:id>', views.racedetails, name='racedetails'),
    path('change/',views.change,name='change')
]
