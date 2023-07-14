from django.shortcuts import render, HttpResponse, redirect
from django.http import HttpRequest
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from User.models import UserProfile
from User.forms import LoginForm

# Create your views here.
class Login(View):
    def get(self, request : HttpRequest):
        fm = LoginForm()
        return render(request, "User/login.html", {'form':fm, 'pwd_err':""})
    
    def post(self, request : HttpRequest):
        # username = request.POST.get('username')
        # pwd = request.POST.get('pwd')
        fm = LoginForm(request.POST)
        if not fm.is_valid():
            return render(request, "User/login.html", {'form':fm, 'pwd_err':""})
        else:
            username = fm.cleaned_data.get('username')
            pwd = fm.cleaned_data.get('password')
            user = authenticate(username = username, password = pwd)
            if user is None:
                return render(request, "User/login.html", {'form':fm, 'pwd_err':"密码错误"})
            else:
                login(request, user)
                path = request.GET.get('next') or '/home/'
                # TODO: 
                return redirect(path)
        

@login_required
def Homepage(request: HttpRequest):
    # 下面那个context只是临时的...后面根据homepage.html更改..
    return render(request, "User/homepage.html", {'request':request})
