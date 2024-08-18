from django.shortcuts import  render,HttpResponse,redirect
from utiles.Tencent.cos import delete_bucket
from web import models
def settings(request,project_id):
    return render(request, 'settings.html')


def delete(request,project_id):
    '''删除项目'''
    if request.method == 'GET':
        return render(request, 'settings_delete.html')
    else:
        project_name = request.POST.get('project_name')
        if not project_name or project_name != request.project.name:
            return render(request, 'settings_delete.html',{'error':'项目名错误'})
        '''项目名写对了'''
        if request.tracer != request.project.creator:
            return render(request, 'settings_delete.html',{'error':'只有项目创建者可以删除'})

        '''删除桶中的文件和碎片'''
        '''删除桶'''
        delete_bucket(request.project.bucket,request.project.region)
        models.Project.objects.filter(id=request.project.id).delete()

        return redirect('project_list')




