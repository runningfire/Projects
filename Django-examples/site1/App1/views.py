from django.shortcuts import render

def index(request):
    return render(request, 'app1n/homePage.html')


# Create your views here.
