from django.shortcuts import render, HttpResponse, redirect
from django.http import HttpRequest
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from User.models import UserProfile
from User.forms import LoginForm, MyUserCreationForm

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
            

class Register(View):
    '''
    注册用。用auth自带的UserCreationForm表单实现.  
    UserCreationField有三个fields: username(of User model), password1, password2.
    '''
    def get(self, request:HttpRequest):
        form = MyUserCreationForm()
        return render(request, 'User/register.html', {'form':form})
    
    def post(self, request:HttpRequest):
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)   # 创建新用户了.
            # TODO: 初始化第一张默认图!
            #user.graph_roots = bytearray([0x00])
            user.save()
            return redirect('/register/success/')
        else:
            return render(request, 'User/register.html', {'form':form})
        

class RegisterSuccess(View):
    '''
    登录成功显示的界面，只有跳转到登录界面的一个链接是有用的。
    如果可以的话，登录成功后应该弹出一个模态框，关闭模态框之后自动回到登录界面比较好.
    '''
    def get(self, request:HttpRequest):
        return render(request, 'User/register_success.html')

        

@login_required
def Homepage(request: HttpRequest):
    # 下面那个context只是临时的...后面根据homepage.html更改..
    thisuser = UserProfile.objects.get(username = request.user.username)
    return render(request, "User/homepage.html", {'user':thisuser})
