#coding:utf-8
__author__ = "dfk"
__date__ = "2017/12/15 11:05"

from django.conf.urls import url, include

from .views import CourseListView,CourseDetailView,CourseInfoView,CommentsView,AddCommentsView,VideoPalyView

app_name = 'courses'
urlpatterns = [
    #课程列表页
    url(r'^list/$',CourseListView.as_view(),name='course_list'),

    #课程详情页
    url(r'^detail/(?P<course_id>\d+)/$',CourseDetailView.as_view(),name='course_detail'),

    url(r'^info/(?P<course_id>\d+)/$', CourseInfoView.as_view(), name='course_info'),

    #课程评论
    url(r'^comment/(?P<course_id>\d+)/$', CommentsView.as_view(), name='course_comment'),

    #添加课程评论
    url(r'^add_comments/$', AddCommentsView.as_view(), name='add_comments'),

    #播放
    url(r'^video/(?P<video_id>\d+)/$', VideoPalyView.as_view(), name='course_play'),
    #播放评论
    url(r'^video_comment/(?P<course_id>\d+)/$', CommentsView.as_view(), name='video_comment'),


]
