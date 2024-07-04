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
        form = account.RegisterModelForm(data=request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            instance = form.save()
            return JsonResponse({'status':True,'data':'/login/sms'})
        else:
            return JsonResponse({'status': False, 'error': form.errors})



def send_sms(request):
    '''发送短信'''
    #form会帮我去校验 手机号是否为空等
    form = account.SendSmsForm(request,data=request.GET)
    if form.is_valid():
       return JsonResponse({'status':True})
      #发短信
      #redis
    return JsonResponse({'status':False,'error':form.errors})


def login_sms(request):
    '''短信登录'''
    if request.method == 'GET':
          form = account.LoginSmsForm()
          return  render(request,'login_sms.html',{'form' : form})
    else:
        form = account.LoginSmsForm(data=request.POST)
        if form.is_valid():
            user_object = form.cleaned_data['mobile_phone']
            return JsonResponse({'status': True, 'data': '/index/'})
        else:
            return JsonResponse({'status': False, 'error': form.errors})


def login(request):
    '''用户名密码登录'''
    if request.method == 'GET':
        form = account.LoginForm()
        return render(request, 'login.html', {'form': form})
    else:
        form = account.LoginSmsForm(data=request.POST)
        if form.is_valid():
            user_object = form.cleaned_data['mobile_phone']
            return JsonResponse({'status': True, 'data': '/index/'})
        else:
            return JsonResponse({'status': False, 'error': form.errors})
def index(request):
    return  render(request,'index.html')

def image_code(request):
    '''生成图片验证码'''
    from utiles.image_code import  check_code
    from io import BytesIO


    image_object,code = check_code()
    stream = BytesIO()
    image_object.save(stream, 'png')
    return HttpResponse(stream.getvalue())



