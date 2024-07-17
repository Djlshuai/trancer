from django.conf.urls import url,include
from web.views import account
from web.views import home
from web.views import project
from web.views import manage
from web.views import wiki
from web.views import file

urlpatterns = [
    url(r'^register/$',account.register ,name='register'),
    url(r'^send/sms/$', account.send_sms, name='send_sms'),
    url(r'^login/sms/$', account.login_sms, name='login_sms'),
    url(r'^login/$', account.login, name='login'),
    url(r'^image/code/$', account.image_code, name='image_code'),
    url(r'^index/$', home.index, name='index'),
    url(r'^logout/$', account.logout, name='logout'),

    #项目列表
    url(r'^project/list/$', project.project_list, name='project_list'),
    url(r'^project/star/(?P<project_type>\w+)/(?P<project_id>\d+)/$', project.project_star, name='project_star'),
    url(r'^project/unstar/(?P<project_type>\w+)/(?P<project_id>\d+)/$', project.project_unstar, name='project_unstar'),

    #项目管理
    url(r'^manage/(?P<project_id>\d+)/dashboard/$', manage.dashboard, name='dashboard'),
    url(r'^manage/(?P<project_id>\d+)/issues/$', manage.issues, name='issues'),
    url(r'^manage/(?P<project_id>\d+)/statistics/$', manage.statistics, name='statistics'),

    url(r'^manage/(?P<project_id>\d+)/wiki/$', wiki.wiki, name='wiki'),
    url(r'^manage/(?P<project_id>\d+)/wiki/add/$', wiki.wiki_add, name='wiki_add'),
    url(r'^manage/(?P<project_id>\d+)/wiki/catalog/$', wiki.wiki_catalog, name='wiki_catalog'),
    url(r'^manage/(?P<project_id>\d+)/wiki/catalog/$', wiki.wiki_catalog, name='wiki_catalog'),
    url(r'^manage/(?P<project_id>\d+)/wiki/delete/(?P<wiki_id>\d+)/$', wiki.wiki_delete, name='wiki_delete'),
    url(r'^manage/(?P<project_id>\d+)/wiki/edit/(?P<wiki_id>\d+)/$', wiki.wiki_edit, name='wiki_edit'),
    url(r'^manage/(?P<project_id>\d+)/wiki/upload/$', wiki.wiki_upload, name='wiki_upload'),

    url(r'^manage/(?P<project_id>\d+)/file/$', file.file, name='file'),
    url(r'^manage/(?P<project_id>\d+)/file/delete/$', file.file_delete, name='file_delete'),
    url(r'^manage/(?P<project_id>\d+)/cos/credential/$', file.cos_credential, name='cos_credential'),

    url(r'^manage/(?P<project_id>\d+)/settings/$', manage.settings, name='settings'),

]