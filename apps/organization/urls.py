# coding:utf-8
__author__ = "dfk"
__date__ = "2017/12/14 9:53"

from django.conf.urls import url, include
from .views import OrgView,AddUserAskView,OrgHomeView,OrgCourseView,OrgDescView,OrgTeacherView,AddFavView

app_name = 'organization'
urlpatterns = [
    # 课程机构列表页
    url('^list/$', OrgView.as_view(), name='org_list'),
    url('^add_ask/$',AddUserAskView.as_view(),name='add_ask'),
    url('^home/(?P<org_id>\d+)/$',OrgHomeView.as_view(),name='org_home'),
    url('^course/(?P<org_id>\d+)/$',OrgCourseView.as_view(),name='org_course'),
    url('^desc/(?P<org_id>\d+)/$',OrgDescView.as_view(),name='org_desc'),
    url('^org_teacher/(?P<org_id>\d+)/$',OrgTeacherView.as_view(),name='org_teacher'),

    #机构收藏
    url('^add_fav/$', AddFavView.as_view(), name='add_fav'),

]
