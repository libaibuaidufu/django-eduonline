# coding:utf-8
import json

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.views.generic.base import View
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, HttpResponseRedirect
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
# from django.urls import reverse
from django.core.urlresolvers import reverse

from .models import UserProfile, EmailVerifyRecord, Banner
from .forms import LoginForm, RegisterForm, ForgetForm, ModifyPwdForm, UploadImageForm, UserinfoForm
from utils.email_send import send_register_email
from utils.mixin_utils import LoginRequiredMixin
from operation.models import UserCourse, UserFacorite, UserMessage
from organization.models import CourseOrg, Teacher
from courses.models import Course


# 自定义验证
class CustomBackend(ModelBackend):
    pass
    # def authenticate(self, request, username=None, password=None, **kwargs):
    #     try:
    #         user = UserProfile.objects.get(Q(username=username) | Q(email=username))
    #         if user.check_password(password):
    #             return user
    #     except Exception as e:
    #         return None


# 激活
class ActiveUserView(View):
    def get(self, request, active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email
                user = UserProfile.objects.get(email=email)
                user.is_active = True
                user.save()
        else:
            return render(request, 'active_fail.html')
        return render(request, 'login.html')


# 注册
class RegisterView(View):
    def get(self, request):
        register_form = RegisterForm()
        return render(request, 'register.html', {'register_form': register_form})

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user_name = request.POST.get("email", "")
            if UserProfile.objects.filter(email=user_name):
                return render(request, "register.html", {"register_form": register_form, "msg": "用户已经存在"})
            pass_word = request.POST.get("password", "")
            user_profile = UserProfile()
            user_profile.username = user_name
            user_profile.email = user_name
            user_profile.password = make_password(pass_word)
            user_profile.is_active = False
            user_profile.save()

            # 写入欢迎注册的信息
            user_message = UserMessage()
            user_message.user = user_profile.id
            user_message.message = "欢迎注册幕学在线网"
            user_message.save()

            send_register_email(user_name, "register")
            return render(request, 'login.html', {})
        else:
            return render(request, "register.html", {"register_form": register_form})


# 登录
class LoginView(View):
    def get(self, request):
        return render(request, 'login.html', {})

    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user_name = request.POST.get("username", "")
            pass_word = request.POST.get("password", "")
            user = authenticate(username=user_name, password=pass_word)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse('index'))
                else:
                    return render(request, 'login.html', {"msg": "用户未激活！"})
            else:
                return render(request, 'login.html', {"msg": "用户名或者密码错误！"})
        else:
            return render(request, 'login.html', {"login_form": login_form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('index'))


# 忘记密码
class ForgetPwdView(View):
    def get(self, request):
        forget_form = ForgetForm()
        return render(request, "forgetpwd.html", {'forget_form': forget_form})

    def post(self, request):
        forget_form = ForgetForm(request.POST)
        if forget_form.is_valid():
            email = request.POST.get("email", "")
            send_register_email(email, "forget")
            return render(request, 'send_success.html')
        else:
            return render(request, "forgetpwd.html", {'forget_form': forget_form})


# 重置密码get
class ResetView(View):
    def get(self, request, active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email
                return render(request, 'password_reset.html', {'email': email})
        else:
            return render(request, 'active_fail.html')
        return render(request, 'login.html')


# 修改密码post
class ModifyPwdView(View):
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        email = request.POST.get('email', "")
        if modify_form.is_valid():
            pwd1 = request.POST.get("password", "")
            pwd2 = request.POST.get("password2", "")
            if pwd1 != pwd2:
                return render(request, 'password_reset.html', {'email': email, 'msg': '密码不一致'})
            user = UserProfile.objects.get(email=email)
            user.password = make_password(pwd1)
            user.save()

            return render(request, 'login.html')
        else:
            return render(request, 'password_reset.html', {'email': email, 'modify_form': modify_form})


class UserInfoView(LoginRequiredMixin, View):
    '''
    用户个人信息
    '''

    def get(self, request):
        return render(request, 'usercenter-info.html', {})

    def post(self, request):
        user_info_form = UserinfoForm(request.POST, instance=request.user)
        if user_info_form.is_valid():
            user_info_form.save()
            return HttpResponse(json.dumps({'status': 'success', 'msg': '修改成功'}), content_type='application/json')
        else:
            return HttpResponse(json.dumps(user_info_form.errors), content_type='application/json')


class UploadImageView(LoginRequiredMixin, View):
    '''
    用户修改头像
    '''

    # 方法1  #form特性  form中有一个 cleaned_data 可以在debug中断点调试看见 这里面的数据都是验证通过了的
    # def post(self, request):
    #     image_form = UploadImageForm(request.POST, request.FILES)
    #     if image_form.is_valid():
    #         image = image_form.cleaned_data['image']
    #         request.user.image = image
    #         request.user.save()

    # 方法二 利用modelform的特性
    def post(self, request):
        image_form = UploadImageForm(request.POST, request.FILES, instance=request.user)
        if image_form.is_valid():
            image_form.save()
            return HttpResponse(json.dumps({'status': 'success', 'msg': '修改成功'}), content_type='application/json')
        else:
            return HttpResponse(json.dumps({'status': 'fail', 'msg': '修改失败'}), content_type='application/json')


class UpdatePwdView(LoginRequiredMixin, View):
    """
    个人中心修改密码
    """

    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get("password", "")
            pwd2 = request.POST.get("password2", "")
            if pwd1 != pwd2:
                return HttpResponse(json.dumps({'status': 'fail', 'msg': '密码不一致'}), content_type='application/json')
            user = request.user
            user.password = make_password(pwd1)
            user.save()

            return HttpResponse(json.dumps({'status': 'success', 'msg': '修改成功'}), content_type='application/json')
        else:
            return HttpResponse(json.dumps(modify_form.errors), content_type='application/json')


class SendEmailCodeView(LoginRequiredMixin, View):
    """
    发送邮箱验证码
    """

    def get(self, request):
        email = request.GET.get('email', '')

        if UserProfile.objects.filter(email=email):
            return HttpResponse(json.dumps({'status': 'fail', 'email': '邮箱已经存在'}), content_type='application/json')
        send_register_email(email, "update_email")
        return HttpResponse(json.dumps({'status': 'success', 'msg': '修改成功'}), content_type='application/json')


class UpdateEmailView(LoginRequiredMixin, View):
    """
    修改个人邮箱
    """

    def post(self, request):
        email = request.POST.get('email', "")
        code = request.POST.get('code', "")

        existed_records = EmailVerifyRecord.objects.filter(code=code, email=email, send_type='update_email')
        if existed_records:
            user = request.user
            user.email = email
            user.save()
            return HttpResponse(json.dumps({'status': 'success', 'msg': '修改成功'}), content_type='application/json')

        else:
            return HttpResponse(json.dumps({'status': 'fail', 'email': '验证码出错'}), content_type='application/json')


class MyCourseViwe(LoginRequiredMixin, View):
    """
    我的课程
    """

    def get(self, request):
        user_courses = UserCourse.objects.filter(user=request.user).all()
        return render(request, 'usercenter-mycourse.html', {
            'user_courses': user_courses,
        })


class MyfavOrgView(LoginRequiredMixin, View):
    """
    我收藏的机构
    """

    def get(self, request):
        has_fav = 'courseorg'
        userfav_orgs = UserFacorite.objects.filter(user=request.user, fav_type=2)
        userfav_org_ids = [userfav_org.fav_id for userfav_org in userfav_orgs]
        all_userfav_orgs = CourseOrg.objects.filter(id__in=userfav_org_ids)

        return render(request, 'usercenter-fav-org.html', {
            "all_userfav_orgs": all_userfav_orgs,
            'has_fav':has_fav,
        })


class MyfavTeacherView(LoginRequiredMixin, View):
    """
    我收藏的老师
    """

    def get(self, request):
        has_fav = 'teacher'

        userfav_teachers = UserFacorite.objects.filter(user=request.user, fav_type=3)
        userfav_teacher_ids = [userfav_teacher.fav_id for userfav_teacher in userfav_teachers]
        all_userfav_teachers = Teacher.objects.filter(id__in=userfav_teacher_ids)

        return render(request, 'usercenter-fav-teacher.html', {
            "all_userfav_teachers": all_userfav_teachers,
            'has_fav': has_fav,
        })


class MyfavCourseView(LoginRequiredMixin, View):
    """
    我收藏的课程
    """

    def get(self, request):
        has_fav = 'courses'
        userfav_courses = UserFacorite.objects.filter(user=request.user, fav_type=1)
        userfav_course_ids = [userfav_course.fav_id for userfav_course in userfav_courses]
        all_userfav_courses = Course.objects.filter(id__in=userfav_course_ids)

        return render(request, 'usercenter-fav-course.html', {
            "all_userfav_courses": all_userfav_courses,
            'has_fav': has_fav,
        })


class MymessageView(LoginRequiredMixin, View):
    """
    我的消息
    """

    def get(self, request):
        all_message = UserMessage.objects.filter(user=request.user.id).all()

        # 用户进入个人消息后清空未读消息的记录
        all_unread_messages = UserMessage.objects.filter(has_read=False, user=request.user.id).all()
        for unread_message in all_unread_messages:
            unread_message.has_read = True
            unread_message.save()

        # 对个人消息进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

            # Provide Paginator with the request object for complete querystring generation
        p = Paginator(all_message, 5, request=request)
        messages = p.page(page)

        return render(request, 'usercenter-message.html', {
            'all_message': messages,
        })


class IndexView(View):
    """
    首页
    """

    def get(self, request):
        # 取出轮播图
        all_banners = Banner.objects.all().order_by('index')

        # 取出公开课
        courses = Course.objects.filter(is_banner=False)[:6]
        banner_courses = Course.objects.filter(is_banner=True)[:3]

        # 取出机构
        all_courseorgs = CourseOrg.objects.all()[:15]

        return render(request, 'index.html', {
            'all_banners': all_banners,
            'courses': courses,
            'banner_courses': banner_courses,
            'all_courseorgs': all_courseorgs,
        })


def page_not_found(request):
    #全局404处理函数
    from django.shortcuts import render_to_response
    response = render_to_response('404.html', {})
    response.status_code = 404
    return response

def page_error(request):
    #全局500处理函数
    from django.shortcuts import render_to_response
    response = render_to_response('500.html',{})
    response.status_code = 500
    return response



# Create your views here.
# def user_login(request):
#     if request.method == "POST":
#         user_name = request.POST.get("username", "")
#         pass_word = request.POST.get("password", "")
#         user = authenticate(username=user_name, password=pass_word)
#         if user is not None:
#             login(request, user)
#             return render(request, 'index.html')
#         else:
#             return render(request, 'login.html', {"msg": "用户名或者密码错误！"})
#     elif request.method == "GET":
#         return render(request, 'login.html', {})
