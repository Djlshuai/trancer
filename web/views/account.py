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
    form = account.RegisterModelForm()
    return render(request,'register.html',{'form' : form})

def send_sms(request):
    '''发送短信'''
    # tpl = request.GET.get('tpl')
    # template_id = settings.TENCENT_SMS_TEMPLATE.get(tpl)
    # if not template_id:
    #     return HttpResponse('模板不存在')
    # code = random.randrange(1000, 9999)
    # res = send_sms_single('15131289', template_id, [code, ])
    # if res['result'] == 0:
    #     return HttpResponse('成功')
    # else:
    #     return HttpResponse(res['errmsg'])
    # pass
    print('doazhel')
    print(request.GET)
    #form会帮我去校验 手机号是否为空等
    form = account.SendSmsForm(request,data=request.GET)
    if form.is_valid():
       return JsonResponse({'status':True})
      #发短信
      #redis
    return JsonResponse({'status':False,'error':form.errors})
