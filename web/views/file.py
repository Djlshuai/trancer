from django.shortcuts import render
from web.forms.file import FolderForm
from django.http import JsonResponse
from web import models
from django.forms import model_to_dict
from utiles.Tencent.cos import delete_file,delete_file_list,credential
import json

def file(request, project_id):
    parent_object = None
    folder_id = request.GET.get('folder', "")
    if folder_id.isdecimal():
        parent_object = models.FileRepository.objects.filter(id=int(folder_id), file_type=2,
                                                             project=request.project).first()
    if request.method == 'GET':
        breadcrumb_list = []
        parent = parent_object
        while parent:
            # breadcrumb_list.insert(0, {'id': parent.id, 'name': parent.name})
            breadcrumb_list.insert(0, model_to_dict(parent, ['id', 'name']))
            parent = parent.parent


        # 当前目录下所有的文件 & 文件夹获取到即可
        queryset = models.FileRepository.objects.filter(project=request.project)
        if parent_object:
            # 进入了某目录
            file_object_list = queryset.filter(parent=parent_object).order_by('-file_type')
        else:
            file_object_list = queryset.filter(parent__isnull=True).order_by('-file_type')
        form = FolderForm(request, parent_object)
        '''文件列表'''
        return render(request, 'file.html', {'form': form,'file_object_list':file_object_list,'breadcrumb_list':breadcrumb_list})
    else:
        fid = request.POST.get('fid', '')
        edit_object = None
        if fid.isdecimal():
            edit_object = models.FileRepository.objects.filter(id=int(fid), file_type=2,
                                                               project=request.project).first()

        if edit_object:
            form = FolderForm(request, parent_object, data=request.POST, instance=edit_object)
        else:
            form = FolderForm(request, parent_object, data=request.POST)
        if form.is_valid():
            form.instance.project = request.project
            form.instance.file_type = 2
            form.instance.update_user = request.tracer
            form.instance.parent = parent_object
            form.save()
            return JsonResponse({'status': True})
        return JsonResponse({'status': False, 'error': form.errors})

def file_delete(request, project_id):
    fid = request.GET.get('fid')
    '''删除文件架及文件，级联删除'''
    delete_object = models.FileRepository.objects.filter(id=int(fid),project=request.project).first()

    if delete_object.file_type == 1:
        '''删文件'''
        request.project.use_space -= delete_object.file_size
        request.project.save()
        delete_file(request.project.bucket, request.project.region, delete_object.key)
        delete_object.delete()
        return JsonResponse({'status': True})

    else:
        '''删除文件夹'''
        total_size = 0
        key_list = []
        folder_list = [delete_object, ]
        for folder in folder_list:
            child_list = models.FileRepository.objects.filter(project=request.project, parent=folder).order_by(
                '-file_type')
            for child in child_list:
                if child.file_type == 2:
                    folder_list.append(child)
                else:
                    # 文件大小汇总
                    total_size += child.file_size
                    # 删除文件
                    key_list.append({"Key": child.key})

    if key_list:
        delete_file_list(request.project.bucket, request.project.region, key_list)

    if total_size:
        request.project.use_space -= total_size
        request.project.save()

    delete_object.delete()
    return JsonResponse({'status': True})

def cos_credential(request,project_id):
    '''获取临时凭证'''
    """ 获取cos上传临时凭证 """
    per_file_limit = request.tracer.price_policy.per_file_size * 1024 * 1024
    total_file_limit = request.tracer.price_policy.project_space * 1024 * 1024 * 1024

    total_size = 0
    file_list = json.loads(request.body.decode('utf-8'))
    for item in file_list:
        # 文件的字节大小 item['size'] = B
        # 单文件限制的大小 M
        # 超出限制
        if item['size'] > per_file_limit:
            msg = "单文件超出限制（最大{}M），文件：{}，请升级套餐。".format(request.tracer.price_policy.per_file_size,
                                                                       item['name'])
            return JsonResponse({'status': False, 'error': msg})
        total_size += item['size']

        # 做容量限制：单文件 & 总容量

    # 总容量进行限制
    # request.tracer.price_policy.project_space  # 项目的允许的空间
    # request.tracer.project.use_space # 项目已使用的空间
    if request.project.use_space + total_size > total_file_limit:
        return JsonResponse({'status': False, 'error': "容量超过限制，请升级套餐。"})

    data_dict = credential(request.project.bucket, request.project.region)
    return JsonResponse({'status': True, 'data': data_dict})
