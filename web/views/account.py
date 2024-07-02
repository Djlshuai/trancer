# 用户注册,登录,
from django.shortcuts import render
from web.forms import account
from django.http import HttpResponse,JsonResponse
import random
from django.conf import settings
def register(request):
    '''
    注册
    '''
    if request.method == 'GET':
        form = account.RegisterModelForm()
        return render(request,'register.html',{'form' : form})
    else:
        print(request.POST)
        return JsonResponse({})

def send_sms(request):
    '''发送短信'''
    #form会帮我去校验 手机号是否为空等
    form = account.SendSmsForm(request,data=request.GET)
    if form.is_valid():
       return JsonResponse({'status':True})
      #发短信
      #redis
    return JsonResponse({'status':False,'error':form.errors})
