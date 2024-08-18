from django.shortcuts import render,HttpResponse,redirect
from web.forms.project import ProjectModelForm
from web.forms.issues import InviteModelForm
from web import models
from django.http import JsonResponse
from utiles.Tencent import cos
import time
from django.views.decorators.csrf import csrf_exempt
from utiles.encrypt import uid
from django.urls import reverse
import datetime


def project_list(request):
    if request.method == 'GET':
        project_dict = {'star': [], 'my': [], 'join': []}
        my_project_list = models.Project.objects.filter(creator=request.tracer)
        for row in my_project_list:
            if row.star:
                project_dict['star'].append({"value":row,"type":"my"})
            else:
                project_dict['my'].append(row)

        join_project_list = models.ProjectUser.objects.filter(user=request.tracer)
        for item in join_project_list:
            if item.star:
                project_dict['star'].append({"value":item.project,"type":"join"})
            else:
                project_dict['join'].append(item.project)
        form = ProjectModelForm(request)
        return render(request, 'project_list.html', {'form': form, 'project_dict': project_dict})
    else:
        form = ProjectModelForm(request,data=request.POST)
        if form.is_valid():
            '''为项目存储桶'''
            timestamp = int(time.time())
            name = form.cleaned_data['name']
            bucket = "{}-{}-1317059587".format(name,timestamp)
            region = 'ap-guangzhou'
            cos.create_bucket(bucket,region)

            '''创建项目'''
            form.instance.region = region
            form.instance.bucket = bucket
            form.instance.creator = request.tracer
            instance =form.save()

            '''项目初始化问题类型'''
            issue_type_object_list=[]
            for item in models.IssuesType.PROJECT_INIT_LIST:
                issue_type_object_list.append(models.IssuesType(project=instance,title=item))
            models.IssuesType.objects.bulk_create(issue_type_object_list)
            return JsonResponse({'status':True})
        else:
            return JsonResponse({'status': False, 'error': form.errors})

def project_star(request,project_type,project_id):
    if project_type == 'my':
        models.Project.objects.filter(id=project_id,creator=request.tracer).update(star=True)
        return redirect('project_list')

    if project_type == 'join':
        models.ProjectUser.objects.filter(id=project_id,user=request.tracer).update(star=True)
        return redirect('project_list')
    return  HttpResponse('非法分子')


def project_unstar(request,project_type,project_id):
    if project_type == 'my':
        models.Project.objects.filter(id=project_id, creator=request.tracer).update(star=False)
        return redirect('project_list')

    if project_type == 'join':
        models.ProjectUser.objects.filter(id=project_id, user=request.tracer).update(star=False)
        return redirect('project_list')
    return HttpResponse('非法分子')

@csrf_exempt
def invite_url(request,project_id):
    """ 生成邀请码 """

    form = InviteModelForm(data=request.POST)
    if form.is_valid():
        """
        1. 创建随机的邀请码
        2. 验证码保存到数据库
        3. 限制：只有创建者才能邀请
        """
        if request.tracer != request.project.creator:
            form.add_error('period', "无权创建邀请码")
            return JsonResponse({'status': False, 'error': form.errors})

        random_invite_code = uid(request.tracer.mobile_phone)
        form.instance.project = request.project
        form.instance.code = random_invite_code
        form.instance.creator = request.tracer
        form.save()
        # 将验邀请码返回给前端，前端页面上展示出来。
        url = "{scheme}://{host}{path}".format(
            scheme=request.scheme,
            host=request.get_host(),
            path=reverse('invite_join', kwargs={'code': random_invite_code})
        )

        return JsonResponse({'status': True, 'data': url})

    return JsonResponse({'status': False, 'error': form.errors})


def invite_join(request,code):
    form = InviteModelForm(data=request.POST)
    if form.is_valid():
        """
        1. 创建随机的邀请码
        2. 验证码保存到数据库
        3. 限制：只有创建者才能邀请
        """
        if request.tracer.user != request.tracer.project.creator:
            form.add_error('period', "无权创建邀请码")
            return JsonResponse({'status': False, 'error': form.errors})

        random_invite_code = uid(request.tracer.user.mobile_phone)
        form.instance.project = request.tracer.project
        form.instance.code = random_invite_code
        form.instance.creator = request.tracer.user
        form.save()

        # 将验邀请码返回给前端，前端页面上展示出来。
        url = "{scheme}://{host}{path}".format(
            scheme=request.scheme,
            host=request.get_host(),
            path=reverse('invite_join', kwargs={'code': random_invite_code})
        )

        return JsonResponse({'status': True, 'data': url})

    return JsonResponse({'status': False, 'error': form.errors})


def invite_join(request, code):
    """ 访问邀请码 """
    current_datetime = datetime.datetime.now()

    invite_object = models.ProjectInvite.objects.filter(code=code).first()
    if not invite_object:
        return render(request, 'invite_join.html', {'error': '邀请码不存在'})

    if invite_object.project.creator == request.tracer:
        return render(request, 'invite_join.html', {'error': '创建者无需再加入项目'})

    exists = models.ProjectUser.objects.filter(project=invite_object.project, user=request.tracer).exists()
    if exists:
        return render(request, 'invite_join.html', {'error': '已加入项目无需再加入'})

    # ####### 问题1： 最多允许的成员(要进入的项目的创建者的限制）#######
    # max_member = request.tracer.price_policy.project_member # 当前登录用户他限制

    # 是否已过期，如果已过期则使用免费额度
    max_transaction = models.Transaction.objects.filter(user=invite_object.project.creator).order_by('-id').first()
    if max_transaction.price_policy.category == 1:
        max_member = max_transaction.price_policy.project_member
    else:
        if max_transaction.end_datetime < current_datetime:
            free_object = models.PricePolicy.objects.filter(category=1).first()
            max_member = free_object.project_member
        else:
            max_member = max_transaction.price_policy.project_member

    # 目前所有成员(创建者&参与者）
    current_member = models.ProjectUser.objects.filter(project=invite_object.project).count()
    current_member = current_member + 1
    if current_member >= max_member:
        return render(request, 'invite_join.html', {'error': '项目成员超限，请升级套餐'})

    # 邀请码是否过期？

    limit_datetime = invite_object.create_datetime + datetime.timedelta(minutes=invite_object.period)
    if current_datetime > limit_datetime:
        return render(request, 'invite_join.html', {'error': '邀请码已过期'})

    # 数量限制？
    if invite_object.count:
        if invite_object.use_count >= invite_object.count:
            return render(request, 'invite_join.html', {'error': '邀请码数据已使用完'})
        invite_object.use_count += 1
        invite_object.save()

    models.ProjectUser.objects.create(user=request.tracer, project=invite_object.project)

    # ####### 问题2： 更新项目参与成员 #######
    invite_object.project.join_count += 1
    invite_object.project.save()

    return render(request, 'invite_join.html', {'project': invite_object.project})
