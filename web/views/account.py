# 用户注册,登录,
from django.shortcuts import render
from web.forms import account
def register(request):
    form = account.RegisterModelForm()
    return render(request,'register.html',{'form' : form})