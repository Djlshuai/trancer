from django.conf.urls import url,include
from web.views import account
from web.views import home
from web.views import project
from web.views import manage
from web.views import wiki
from web.views import file
from web.views import setting
from web.views import issues
from web.views import dashboard
urlpatterns = [
    url(r'^register/$',account.register ,name='register'),
    url(r'^send/sms/$', account.send_sms, name='send_sms'),
    url(r'^login/sms/$', account.login_sms, name='login_sms'),
    url(r'^login/$', account.login, name='login'),
    url(r'^image/code/$', account.image_code, name='image_code'),
    url(r'^index/$', home.index, name='index'),
    url(r'^logout/$', account.logout, name='logout'),
    url(r'^price/$', home.price, name='price'),
    url(r'^payment/(?P<policy_id>\d+)/$', home.payment, name='payment'),
    url(r'^pay/$', home.pay, name='pay'),

    #项目列表
    url(r'^project/list/$', project.project_list, name='project_list'),
    url(r'^project/star/(?P<project_type>\w+)/(?P<project_id>\d+)/$', project.project_star, name='project_star'),
    url(r'^project/unstar/(?P<project_type>\w+)/(?P<project_id>\d+)/$', project.project_unstar, name='project_unstar'),

    #项目管理
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
    url(r'^manage/(?P<project_id>\d+)/file/post/$', file.file_post, name='file_post'),
    url(r'^manage/(?P<project_id>\d+)/file/download/(?P<file_id>\d+)/$', file.file_download, name='file_download'),

    url(r'^manage/(?P<project_id>\d+)/settings/$', setting.settings, name='settings'),
    url(r'^manage/(?P<project_id>\d+)/settings/delete/$', setting.delete, name='settings_delete'),

    url(r'^manage/(?P<project_id>\d+)/issues/$', issues.issues, name='issues'),
    url(r'^manage/(?P<project_id>\d+)/invite/url/$', project.invite_url, name='invite_url'),
    url(r'^manage/(?P<project_id>\d+)/issues/detail/(?P<issues_id>\d+)/$', issues.issues_detail, name='issues_detail'),
    url(r'^manage/(?P<project_id>\d+)/issues/record/(?P<issues_id>\d+)/$', issues.issues_record, name='issues_record'),
    url(r'^manage/(?P<project_id>\d+)/issues/change/(?P<issues_id>\d+)/$', issues.issues_change, name='issues_change'),
    url(r'^manage/(?P<project_id>\d+)/dashboard/$', dashboard.dashboard, name='dashboard'),
    url(r'^manage/(?P<project_id>\d+)/dashboard/issues/chart/$', dashboard.issues_chart, name='issues_chart'),


    url(r'^invite/join/(?P<code>\w+)/$', project.invite_join, name='invite_join'),

]