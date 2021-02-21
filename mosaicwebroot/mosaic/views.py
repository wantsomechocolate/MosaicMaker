from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the polls index. Made a change")

def mosaic_view(request, mosaic_name):
	return HttpResponse("Hello, you're trying to view: " + mosaic_name)