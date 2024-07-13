import json

from django.shortcuts import render, redirect
from web.forms.wiki import WikeModelForm
from django.urls import reverse
from web import models
from django.http import JsonResponse


def wiki(request, project_id):
    wiki_id = request.GET.get('wiki_id')
    if not wiki_id or not wiki_id.isdecimal():
        return render(request, 'wiki.html')
    wiki_object = models.Wiki.objects.filter(id=wiki_id, project_id=project_id).first()
    return render(request, 'wiki.html',{'wiki_object':wiki_object})


def wiki_add(request, project_id):
    if request.method == 'GET':
        form = WikeModelForm(request)
        data = models.Wiki.objects.all().values("id", "title", "parent_id").filter(project_id=project_id)
        data = json.dumps(list(data))
        return render(request, 'wiki_form.html', {'form': form, 'data': data})
    else:
        form = WikeModelForm(request, data=request.POST)
        if form.is_valid():
            '''判断是否选择了父文章'''
            if form.instance.parent:
                form.instance.depth = form.instance.parent.depth + 1
            else:
                form.instance.depth = 1
            form.instance.project = request.project
            form.save()
            url = reverse('wiki', kwargs={'project_id': project_id})
            return redirect(url)
    data = models.Wiki.objects.all().values("id", "title", "parent_id").filter(project_id=project_id)
    data = json.dumps(list(data))
    return render(request, 'wiki_form.html', {'form': form, 'data': data})


def wiki_catalog(request, project_id):
    ''' wiki目录 '''
    data = models.Wiki.objects.all().values("id", "title","parent_id").filter(project_id=project_id).order_by('depth','id')
    return JsonResponse({'status': True, 'data': list(data)})

def wiki_delete(request,project_id,wiki_id):
    models.Wiki.objects.filter(project_id=project_id,id=wiki_id).delete()
    return redirect('wiki', project_id)

def wiki_edit(request,project_id,wiki_id):
    wiki_object = models.Wiki.objects.filter(project_id=project_id,id=wiki_id).first()
    if not  wiki_object:
        return redirect('wiki', project_id)
    if request.method == 'GET':
        form = WikeModelForm(request, instance=wiki_object)
        return render(request, 'wiki_form.html', {'form': form})
    form = WikeModelForm(request, data=request.POST, instance=wiki_object)
    if form.is_valid():
        if form.instance.parent:
            form.instance.depth = form.instance.parent.depth + 1
        else:
            form.instance.depth = 1
        form.save()
        url = reverse('wiki', kwargs={'project_id': project_id})
        previous_url = "{0}?wiki_id={1}".format(url, wiki_id)
        return redirect(previous_url)
    return render(request, 'wiki_form.html', {'form': form})