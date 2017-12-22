# coding:utf-8
__author__ = "dfk"
__date__ = "2017/12/18 11:22"

from django.conf.urls import url, include

from .views import UserInfoView, UploadImageView, UpdatePwdView, SendEmailCodeView
from .views import UpdateEmailView, MyCourseViwe, MyfavOrgView, MyfavTeacherView, MyfavCourseView, MymessageView

app_name = 'users'
urlpatterns = [
    # 用户信息
    url('^info/$', UserInfoView.as_view(), name='user_info'),

    # 用户头像上传
    url('^image/upload/$', UploadImageView.as_view(), name='image_upload'),

    # 用户个人中心修改密码
    url('^update/pwd/$', UpdatePwdView.as_view(), name='update_pwd'),

    # 发送邮箱验证码
    url('^sendemail_code/$', SendEmailCodeView.as_view(), name='sendemail_code'),

    # 修改邮箱
    url('^update_email/$', UpdateEmailView.as_view(), name='update_email'),

    # 我的课程
    url('^mycourse/$', MyCourseViwe.as_view(), name='mycourse'),

    # 我收藏的机构
    url('^myfav_org/$', MyfavOrgView.as_view(), name='myfav_org'),

    # 我收藏的老师
    url('^myfav_teacher/$', MyfavTeacherView.as_view(), name='myfav_teacher'),

    # 我收藏的课程
    url('^myfav_course/$', MyfavCourseView.as_view(), name='myfav_course'),

    # 我的消息
    url('^mymessage/$', MymessageView.as_view(), name='mymessage'),

]
