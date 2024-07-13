from django.shortcuts import render,HttpResponse,redirect
from web.forms.project import ProjectModelForm
from web import models
from django.http import JsonResponse
from utiles.Tencent import cos
import time
from django.views.decorators.csrf import csrf_exempt

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
            form.instance.region = region
            form.instance.bucket = bucket
            form.instance.creator = request.tracer
            form.save()
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