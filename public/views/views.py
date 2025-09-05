from django.shortcuts import render
from django.http import JsonResponse
from artists.models import Location


def get_locations(request):
    locations = Location.objects.all()
    states = list(set(locations.values_list('state', flat=True)))
    cities = list(set(locations.values_list('city', flat=True)))
    return JsonResponse({
        'states': states,
        'cities': cities
    })



