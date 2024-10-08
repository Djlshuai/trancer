from django.template import Library
from web import models
from django.urls import reverse
register = Library()

@register.inclusion_tag('inclusion/all_project_list.html')
def all_project_list(request):
  '''获取我创建的所有项目'''
  my_project_list = models.Project.objects.filter(creator=request.tracer)
  join_project_list = models.ProjectUser.objects.filter(user=request.tracer)
  return {'my':my_project_list,'join':join_project_list,'request':request}


@register.inclusion_tag('inclusion/manage_menu_list.html')
def manage_menu_list(request):
  data_list = [
    {'title': '概览', 'url': reverse("dashboard", kwargs={'project_id': request.project.id})},
    {'title': '问题', 'url': reverse("issues", kwargs={'project_id': request.project.id})},
    {'title': '统计', 'url': reverse("statistics", kwargs={'project_id': request.project.id})},
    {'title': 'wiki', 'url': reverse("wiki", kwargs={'project_id': request.project.id})},
    {'title': '文件', 'url': reverse("file", kwargs={'project_id': request.project.id})},
    {'title': '配置', 'url': reverse("settings", kwargs={'project_id': request.project.id})},
  ]

  for item in data_list:
    # 当前用户访问的URL：request.path_info:  /manage/4/issues/xxx/add/
    if request.path_info.startswith(item['url']):
      item['class'] = 'active'

  return {'data_list': data_list}