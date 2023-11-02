from django.shortcuts import render
from django.http import HttpResponse
from .forms import *
# Create your views here.

def register(request):
   fm=UserRegistration()
   if request.method == 'POST':
      fm = UserRegistration(request.POST)
      print(fm)
      fm.order_fields(field_order=['name','email','password'])
      return render(request, 'userregistration.html', {'form':fm})
   return render(request, 'userregistration.html', {'form':fm})


def home(request):
   return render(request,"login.html")