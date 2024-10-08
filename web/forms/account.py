import random
from django import forms
from web import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.conf import settings
from utiles.Tencent import sms
from django_redis import get_redis_connection
from utiles import encrypt
from web.forms.bootstrap import Bootstrap



class RegisterModelForm(Bootstrap,forms.ModelForm):
    password = forms.CharField(
        label='密码',
        min_length=8,
        max_length=64,
        error_messages={
            'min_length': "密码长度不能小于8个字符",
            'max_length': "密码长度不能大于64个字符"
        },
        widget=forms.PasswordInput()
    )

    confirm_password = forms.CharField(
        label='重复密码',
        min_length=8,
        max_length=64,
        error_messages={
            'min_length': "重复密码长度不能小于8个字符",
            'max_length': "重复密码长度不能大于64个字符"
        },
        widget=forms.PasswordInput())

    mobile_phone = forms.CharField(label='手机号',validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', '手机号格式错误'), ])

    code = forms.CharField(
        label='验证码',
        widget=forms.TextInput())
    class Meta:
        model = models.UserInfo
        fields = ['username', 'email', 'password', 'confirm_password', 'mobile_phone', 'code']


    def clean_username(self):
        username = self.cleaned_data['username']
        exists = models.UserInfo.objects.filter(username=username).exists()
        if exists:
            raise ValidationError('用户名已存在')
            # self.add_error('username','用户名已存在')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        exists = models.UserInfo.objects.filter(email=email).exists()
        if exists:
            raise ValidationError('邮箱已存在')
        return email

    def clean_password(self):
        pwd = self.cleaned_data['password']
        # 加密 & 返回
        return encrypt.md5(pwd)


    def clean_confirm_password(self):
        pwd = self.cleaned_data.get('password')

        confirm_pwd = encrypt.md5(self.cleaned_data['confirm_password'])
        # confirm_pwd = self.cleaned_data.get('confirm_pwd')
        if pwd != confirm_pwd:
            raise ValidationError('两次密码不一致')

        return confirm_pwd

    def clean_mobile_phone(self):
        mobile_phone = self.cleaned_data['mobile_phone']
        exists = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        if exists:
            raise ValidationError('手机号已注册')
        return mobile_phone

    def clean_code(self):
        code = self.cleaned_data['code']

        # mobile_phone = self.cleaned_data['mobile_phone']

        mobile_phone = self.cleaned_data.get('mobile_phone')
        if not mobile_phone:
            return code

        conn = get_redis_connection()
        redis_code = conn.get(mobile_phone)
        if not redis_code:
            raise ValidationError('验证码失效或未发送，请重新发送')

        redis_str_code = redis_code.decode('utf-8')

        if code.strip() != redis_str_code:
            raise ValidationError('验证码错误，请重新输入')

        return code
#只做表单验证
class SendSmsForm(forms.Form):
    mobile_phone = forms.CharField(label='手机号',validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', '手机号格式错误'), ])

    def __init__(self,request,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.request = request

    def clean_mobile_phone(self):
        '''手机号校验的钩子函数'''
        mobile_phone = self.cleaned_data['mobile_phone']

        #判断短信模板
        tpl = self.request.GET.get('tpl')
        template_id = settings.TENCENT_SMS_TEMPLATE.get(tpl)
        if not template_id:
            raise ValidationError('模板错误')

        #校验数据库中是否已有手机号
        if tpl == 'login':
            exists = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
            if not exists:
                raise ValidationError('手机号不存在')
        else:
            exists = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
            if exists :
                raise  ValidationError('手机号存在')

        #发短信&redis
        code = random.randrange(1000,9999)
        # res = sms.send_sms_single(mobile_phone,template_id,[code,])
        # if res['result'] != 0 :
        #     err = res['errmsg']
        #     raise ValidationError(f'短信发送失败:{err}')
        print(f'验证码为{code}')
        conn = get_redis_connection()
        conn.set(mobile_phone,code,ex=60)

        return mobile_phone

class LoginSmsForm(Bootstrap,forms.Form):
    mobile_phone = forms.CharField(label='手机号',validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', '手机号格式错误'), ])
    code = forms.CharField(
    label='验证码',
    widget=forms.TextInput())
    def clean_mobile_phone(self):
        mobile_phone = self.cleaned_data['mobile_phone']
        user_object = models.UserInfo.objects.filter(mobile_phone=mobile_phone).first()
        if not user_object:
            raise ValidationError('手机号不存在')
        return user_object

    def clean_code(self):
        code = self.cleaned_data['code']

        # mobile_phone = self.cleaned_data['mobile_phone']

        user_object = self.cleaned_data.get('mobile_phone')
        if not user_object:
            return code

        conn = get_redis_connection()
        redis_code = conn.get(user_object.mobile_phone)
        if not redis_code:
            raise ValidationError('验证码失效或未发送，请重新发送')

        redis_str_code = redis_code.decode('utf-8')

        if code.strip() != redis_str_code:
            raise ValidationError('验证码错误，请重新输入')

        return code

class LoginForm(Bootstrap,forms.Form):
    username = forms.CharField(label='邮箱或手机号')
    password = forms.CharField(label='密码', widget=forms.PasswordInput(render_value=True))
    code = forms.CharField(label='图片验证码')

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_password(self):
        pwd = self.cleaned_data['password']
        # 加密 & 返回
        return encrypt.md5(pwd)

    def clean_code(self):
        """ 钩子 图片验证码是否正确？ """
        # 读取用户输入的yanzhengm
        code = self.cleaned_data['code']

        # 去session获取自己的验证码
        session_code = self.request.session.get('imgae_code')
        if not session_code:
            raise ValidationError('验证码已过期，请重新获取')

        if code.strip().upper() != session_code.strip().upper():
            raise ValidationError('验证码输入错误')

        return code