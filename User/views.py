from django.shortcuts import render, HttpResponse, redirect
from django.http import HttpRequest
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from User.models import UserProfile

# Create your views here.
class Login(View):
    def get(self, request : HttpRequest):
        return render(request, "User/login.html")
    
    def post(self, request : HttpRequest):
        username = request.POST.get('username')
        pwd = request.POST.get('pwd')
        user = authenticate(username = username, password = pwd)
        if user is None:
            return redirect('/login/')
        else:
            login(request, user)
            path = request.GET.get('next') or '/home/'
            # TODO: 
            return redirect(path)
        

@login_required
def Homepage(request: HttpRequest):
    # 下面那个context只是临时的...后面根据homepage.html更改..
    return render(request, "User/homepage.html", {'request':request})
