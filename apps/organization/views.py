# coding:utf-8
import json

from django.shortcuts import render
from django.views.generic import View
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.db.models import Q

from .models import CourseOrg, CityDict, Teacher
from .forms import UserAskForm
from courses.models import Course
from operation.models import UserFacorite


# Create your views here.

class OrgView(View):
    """
    课程机构列表功能
    """

    def get(self, request):
        # 课程机构
        all_orgs = CourseOrg.objects.all()
        hot_orgs = all_orgs.order_by("-click_nums")[:3]
        # 城市
        all_citys = CityDict.objects.all()

        # 机构搜索
        search_keywords = request.GET.get('keywords', "")
        if search_keywords:
            all_orgs = all_orgs.filter(
                Q(name__icontains=search_keywords) | Q(desc__icontains=search_keywords))

        # 取出筛选城市
        city_id = request.GET.get('city', "")
        if city_id:
            all_orgs = all_orgs.filter(city_id=int(city_id))

        # 类别筛选
        category = request.GET.get('ct', '')
        if category:
            all_orgs = all_orgs.filter(category=category)

        # 学习人数
        sort = request.GET.get('sort', '')
        if sort:
            if sort == "students":
                all_orgs = all_orgs.order_by('-students')
            elif sort == 'courses':
                all_orgs = all_orgs.order_by('-course_nums')

        org_nums = all_orgs.count()

        # 对课程机构进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        # Provide Paginator with the request object for complete querystring generation
        p = Paginator(all_orgs, 5, request=request)
        orgs = p.page(page)
        return render(request, 'org-list.html', {
            'all_orgs': orgs,
            'all_citys': all_citys,
            'org_nums': org_nums,
            'city_id': city_id,
            'category': category,
            'hot_orgs': hot_orgs,
            'sort': sort,
        })


class AddUserAskView(View):
    """
    用户添加咨询
    """

    def post(self, request):
        userask_form = UserAskForm(request.POST)
        if userask_form.is_valid():
            user_ask = userask_form.save(commit=True)
            return HttpResponse(json.dumps({'status': 'success'}), content_type='application/json')
        else:
            # return HttpResponse("{'status':'fail','msg':{0}}".format(userask_form.errors),content_type='application/json')
            return HttpResponse(json.dumps({'status': 'fail', 'msg': '添加出错'}), content_type='application/json')


class OrgHomeView(View):
    """
    机构首页
    """

    def get(self, request, org_id):
        current_page = 'home'
        course_org = CourseOrg.objects.get(id=int(org_id))
        course_org.click_nums += 1
        course_org.save()

        has_fav = False
        if request.user.is_authenticated:
            if UserFacorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        all_courses = course_org.course_set.all()[:3]
        all_teachers = course_org.teacher_set.all()[:1]
        return render(request, 'org-detail-homepage.html', {
            'all_courses': all_courses,
            'all_teachers': all_teachers,
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav,
        })


class OrgCourseView(View):
    """
    机构课程列表页
    """

    def get(self, request, org_id):
        current_page = 'course'
        course_org = CourseOrg.objects.get(id=int(org_id))
        has_fav = False
        if request.user.is_authenticated:
            if UserFacorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        all_courses = course_org.course_set.all()
        return render(request, 'org-detail-course.html', {
            'all_courses': all_courses,
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav,
        })


class OrgDescView(View):
    """
    机构介绍
    """

    def get(self, request, org_id):
        current_page = 'desc'
        course_org = CourseOrg.objects.get(id=int(org_id))
        has_fav = False
        if request.user.is_authenticated:
            if UserFacorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        return render(request, 'org-detail-desc.html', {
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav,
        })


class OrgTeacherView(View):
    """
    机构教师页
    """

    def get(self, request, org_id):
        current_page = 'teacher'
        course_org = CourseOrg.objects.get(id=int(org_id))
        has_fav = False
        if request.user.is_authenticated:
            if UserFacorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        all_teachers = course_org.teacher_set.all()
        return render(request, 'org-detail-teachers.html', {
            'all_teachers': all_teachers,
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav,
        })


class AddFavView(View):
    """
    用户收藏，用户取消收藏
    """

    def post(self, request):
        fav_id = request.POST.get('fav_id', 0)
        fav_type = request.POST.get('fav_type', 0)

        if not request.user.is_authenticated:
            # 判断用户登录状态
            return HttpResponse(json.dumps({'status': 'fail', 'msg': '用户未登录'}), content_type='application/json')

        exist_records = UserFacorite.objects.filter(user=request.user, fav_id=int(fav_id), fav_type=int(fav_type))
        if exist_records:
            # 如果记录已经存在，则表示用户取消收藏
            exist_records.delete()
            if int(fav_type) == 1:
                course = Course.objects.get(id=int(fav_id))
                course.fav_nums -= 1
                if course.fav_nums < 0:
                    course.fav_nums = 0
                course.save()
            elif int(fav_type) == 2:
                course_org = CourseOrg.objects.get(id=int(fav_id))
                course_org.fac_nums -= 1
                if course_org.fav_nums < 0:
                    course_org.fav_nums = 0
                course_org.save()
            elif int(fav_type) == 3:
                teacher = Teacher.objects.get(id=int(fav_id))
                teacher.fac_nums -= 1
                if teacher.fav_nums < 0:
                    teacher.fav_nums = 0
                teacher.save()

            # 这里和下面收藏 和已收藏 是为了在前端显示 如果删除了收藏 前端就可以进行收藏
            return HttpResponse(json.dumps({'status': 'success', 'msg': '收藏'}), content_type='application/json')
        else:
            user_fav = UserFacorite()
            if int(fav_id) > 0 and int(fav_type) > 0:
                user_fav.user = request.user
                user_fav.fav_id = int(fav_id)
                user_fav.fav_type = int(fav_type)
                user_fav.save()

                if int(fav_type) == 1:
                    course = Course.objects.get(id=int(fav_id))
                    course.fav_nums += 1
                    course.save()
                elif int(fav_type) == 2:
                    course_org = CourseOrg.objects.get(id=int(fav_id))
                    course_org.fac_nums += 1
                    course_org.save()
                elif int(fav_type) == 3:
                    teacher = Teacher.objects.get(id=int(fav_id))
                    teacher.fac_nums += 1
                    teacher.save()
                # 如果收藏了 前端就显示已收藏 无法再次收藏
                return HttpResponse(json.dumps({'status': 'success', 'msg': '已收藏'}), content_type='application/json')

            else:
                return HttpResponse(json.dumps({'status': 'fail', 'msg': '收藏出错'}), content_type='application/json')


class TeacherView(View):
    def get(self, request):
        # 获取所有教师
        all_teachers = Teacher.objects.all()

        # 热门推荐
        hot_teahcers = Teacher.objects.order_by('-click_nums')[:2]

        # 课程讲师搜索
        search_keywords = request.GET.get('keywords', "")
        if search_keywords:
            all_teachers = all_teachers.filter(
                Q(name__icontains=search_keywords) |
                Q(work_company__icontains=search_keywords) |
                Q(work_position__icontains=search_keywords))

        # 人气排行
        sort = request.GET.get('sort', "")
        if sort:
            if sort == 'hot':
                all_teachers = all_teachers.order_by('-click_nums')

        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

            # Provide Paginator with the request object for complete querystring generation
        p = Paginator(all_teachers, 3, request=request)
        orgs = p.page(page)

        return render(request, 'teachers-list.html', {
            'all_teachers': orgs,
            'hot_teahcers': hot_teahcers,
            'sort': sort,
        })


class TeacherDetailView(View):
    def get(self, request, teacher_id):
        teacher = Teacher.objects.get(id=teacher_id)
        teacher.click_nums += 1
        teacher.save()

        hot_teahcers = Teacher.objects.order_by('-click_nums')[:2]

        has_fav_teacher = False
        has_fav_org = False

        if request.user.is_authenticated:
            if UserFacorite.objects.filter(user=request.user, fav_id=teacher.id, fav_type=3):
                has_fav_teacher = True
            if UserFacorite.objects.filter(user=request.user, fav_id=teacher.org.id, fav_type=2):
                has_fav_org = True

        return render(request, 'teacher-detail.html', {
            'teacher': teacher,
            'hot_teahcers': hot_teahcers,
            'has_fav_teacher': has_fav_teacher,
            'has_fav_org': has_fav_org,
        })
