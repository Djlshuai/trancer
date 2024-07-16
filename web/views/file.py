from django.shortcuts import render
from web.forms.file import FolderForm
from django.http import JsonResponse
from web import models
from django.forms import model_to_dict

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
