from django.shortcuts import render
from django.http import HttpResponse

def exp(request):
    return HttpResponse('<h3>Привет Мир!</h3>')
