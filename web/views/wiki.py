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
    print(wiki_object.content)
    return render(request, 'wiki.html',{'wiki_object':wiki_object})


def wiki_add(request, project_id):
    if request.method == 'GET':
        form = WikeModelForm(request)
        data = models.Wiki.objects.all().values("id", "title", "parent_id").filter(project_id=project_id)
        data = json.dumps(list(data))
        return render(request, 'wiki_add.html', {'form': form, 'data': data})
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
    return render(request, 'wiki_add.html', {'form': form, 'data': data})


def wiki_catalog(request, project_id):
    ''' wiki目录 '''
    data = models.Wiki.objects.all().values("id", "title","parent_id").filter(project_id=project_id).order_by('depth','id')
    return JsonResponse({'status': True, 'data': list(data)})
