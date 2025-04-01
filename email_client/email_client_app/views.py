from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def test_view(request):
    return HttpResponse('Email App is working!')

def index(request):
    return render(request, 'email_client_app/index.html')
