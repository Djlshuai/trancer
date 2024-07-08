from django.shortcuts import render
from web.forms.project import ProjectModelForm
from web import models
from django.http import JsonResponse

def project_list(request):
    if request.method == 'GET':
        form = ProjectModelForm(request)
        return render(request, 'project_list.html', {'form': form})
    else:
        form = ProjectModelForm(request,data=request.POST)
        if form.is_valid():
            form.instance.creator = request.tracer
            form.save()
            # print(form.cleaned_data)
            # instance = form.save()
            # policy_object = models.PricePolicy.objects.filter(category=1, title="个人免费版").first()
            # models.Transaction.objects.create(
            #     status=2,
            #     order=str(uuid.uuid4()),
            #     user=instance,
            #     price_policy=policy_object,
            #     count=0,
            #     price=0,
            #     start_datetime=datetime.datetime.now()
            # )
            return JsonResponse({'status':True})
        else:
            return JsonResponse({'status': False, 'error': form.errors})