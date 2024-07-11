
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from web import models
from django.shortcuts import redirect
import datetime

class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request):

        """ 如果用户已登录，则request中赋值 """
        user_id =request.session.get('user_id',0)
        user_object = models.UserInfo.objects.filter(id=user_id).first()
        request.tracer = user_object

        '''白名单，没有登陆都可以访问的'''
        if request.path_info in settings.WHITE_REGEX_URL_LIST:
            return
        if not request.tracer:
            return redirect('login')

        '''拿到用户免费额度'''
        _object = models.Transaction.objects.filter(user=user_object,status=2).order_by('-id').first()
        current_time = datetime.datetime.now()
        if _object.end_datetime and _object.end_datetime < current_time:
            _object = models.Transaction.objects.filter(user=user_object,status=2,price_policy__category=1).order_by('id').first()
        request.tracer.price_policy = _object.price_policy

    def process_view(self, request, view, args,kwargs):
        #判断是url是不是manage开头的
        '''如果不是就继续执行'''
        if not request.path_info.startswith('/manage/'):
            return
        project_id = kwargs.get('project_id')

        '''判断是不是我创建的'''
        project_project = models.Project.objects.filter(creator=request.tracer,id=project_id).first()
        if project_project:
            request.project=project_project
            return

        '''判断是不是我参与的'''
        project_user = models.ProjectUser.objects.filter(user=request.tracer,project_id=project_id).first()
        if project_user:
            request.project = project_user.project
            return

        '''如果都不是'''
        return redirect('project_list')
