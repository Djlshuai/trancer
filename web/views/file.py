from django.shortcuts import render, HttpResponse
from web.forms.file import FolderForm,FileModelForm
from django.http import JsonResponse
from web import models
from django.forms import model_to_dict
from utiles.Tencent.cos import delete_file,delete_file_list,credential
import json
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import requests
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
        return render(request, 'file.html', {
            'form': form,'file_object_list':file_object_list,'breadcrumb_list':breadcrumb_list,'folder_object':parent_object})
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

@csrf_exempt
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

@csrf_exempt
def file_post(request, project_id):
    """ 已上传成功的文件写入到数据 """
    """
    name: fileName,
    key: key,
    file_size: fileSize,
    parent: CURRENT_FOLDER_ID,
    # etag: data.ETag,
    file_path: data.Location
    """

    # 根据key再去cos获取文件Etag和"db7c0d83e50474f934fd4ddf059406e5"

    print(request.POST)
    # 把获取到的数据写入数据库即可
    form = FileModelForm(request, data=request.POST)
    if form.is_valid():
        # 通过ModelForm.save存储到数据库中的数据返回的isntance对象，无法通过get_xx_display获取choice的中文
        # form.instance.file_type = 1
        # form.update_user = request.tracer.user
        # instance = form.save() # 添加成功之后，获取到新添加的那个对象（instance.id,instance.name,instance.file_type,instace.get_file_type_display()

        # 校验通过：数据写入到数据库
        data_dict = form.cleaned_data
        data_dict.pop('etag')
        data_dict.update({'project': request.project, 'file_type': 1, 'update_user': request.tracer})
        instance = models.FileRepository.objects.create(**data_dict)

        # 项目的已使用空间：更新 (data_dict['file_size'])
        request.project.use_space += data_dict['file_size']
        request.project.save()

        result = {
            'id': instance.id,
            'name': instance.name,
            'file_size': instance.file_size,
            'username': instance.update_user.username,
            'datetime': instance.update_datetime.strftime('%Y{y}%m{m}%d{d} %H{h}%M{f}%S{s}').format(y='年',m='月',d='日',h='时',f='分',s='秒'),
            'download_url': reverse('file_download', kwargs={"project_id": project_id, 'file_id': instance.id})
            # 'file_type': instance.get_file_type_display()
        }
        return JsonResponse({'status': True, 'data': result})

    return JsonResponse({'status': False, 'data': "文件错误"})


def file_download(request,project_id,file_id):
    """ 下载文件 """
    file_object = models.FileRepository.objects.filter(id=file_id, project_id=project_id).first()
    res = requests.get(file_object.file_path)

    # 文件分块处理（适用于大文件）     @孙歆尧
    data = res.iter_content()

    # 设置content_type=application/octet-stream 用于提示下载框        @孙歆尧
    response = HttpResponse(data, content_type="application/octet-stream")
    from django.utils.encoding import escape_uri_path

    # 设置响应头：中文件文件名转义      @王洋
    response['Content-Disposition'] = "attachment; filename={};".format(escape_uri_path(file_object.name))
    return response