# coding:utf-8
import json

from django.shortcuts import render
from django.views.generic.base import View
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.db.models import Q

from .models import Course, CourseResource, Video
from operation.models import UserFacorite, CourseComments, UserCourse
from utils.mixin_utils import LoginRequiredMixin


# Create your views here.


class CourseListView(View):
    def get(self, request):
        # 全部课程
        all_courses = Course.objects.all().order_by('-add_time')

        # 侧栏热门推荐
        hot_courses = Course.objects.order_by('-click_nums')[:3]

        # 课程搜索
        search_keywords = request.GET.get('keywords', "")
        if search_keywords:
            all_courses = all_courses.filter(
                Q(name__icontains=search_keywords) | Q(desc__icontains=search_keywords) | Q(
                    detail__icontains=search_keywords))

        sort = request.GET.get('sort', "")
        if sort:
            if sort == 'hot':
                # 热门筛选
                all_courses = all_courses.order_by('-click_nums')
            if sort == 'students':
                # 人数筛选
                all_courses = all_courses.order_by('-students')

        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        # Provide Paginator with the request object for complete querystring generation
        p = Paginator(all_courses, 1, request=request)
        orgs = p.page(page)

        return render(request, 'course-list.html', {
            'all_courses': orgs,
            'hot_courses': hot_courses,
            'sort': sort,
        })


class VideoPalyView(View):
    """
    视频播放页面
    """

    def get(self, request, video_id):
        video = Video.objects.get(id=int(video_id))
        course = video.lesson.course

        # 查询用户是否已经关联了该课程
        user_cousers = UserCourse.objects.filter(course=course)
        if not user_cousers:
            user_couser = UserCourse(user=request.user, course=course)
            user_couser.save()

        user_cousers = UserCourse.objects.filter(course=course)
        user_ids = [user_couser.user.id for user_couser in user_cousers]
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        # 取出所有课程id
        course_ids = [user_couser.course.id for user_couser in all_user_courses]
        # 获取学过该课程的同学学过其他的课程
        relate_courses = Course.objects.filter(id__in=course_ids).order_by('-click_nums')[:5]

        all_resources = CourseResource.objects.filter(course=course)
        return render(request, 'course-play.html', {
            'course': course,
            'all_resources': all_resources,
            'relate_courses': relate_courses,
            'video': video,
        })


class VideoCommentView(VideoPalyView, View):
    pass


class CourseDetailView(View):
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))

        # 增加课程点击数
        course.click_nums += 1
        course.save()

        has_fav_course = False
        has_fav_org = False

        if request.user.is_authenticated:
            if UserFacorite.objects.filter(user=request.user, fav_id=course.id, fav_type=1):
                has_fav_course = True
            if UserFacorite.objects.filter(user=request.user, fav_id=course.course_org.id, fav_type=2):
                has_fav_org = True

        tag = course.tag
        if tag:
            relate_courses = Course.objects.filter(tag=tag)[:1]
        else:
            relate_courses = []

        return render(request, 'course-detail.html', {
            'course': course,
            'relate_courses': relate_courses,
            'has_fav_org': has_fav_org,
            'has_fav_course': has_fav_course,
        })


class CourseInfoView(LoginRequiredMixin, View):
    """
    课程章节信息
    """

    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        course.click_nums += 1
        course.students += 1
        course.save()

        # 查询用户是否已经关联了该课程
        user_cousers = UserCourse.objects.filter(course=course,user=request.user)
        if not user_cousers:
            user_couser = UserCourse(user=request.user, course=course)
            user_couser.save()

        user_cousers = UserCourse.objects.filter(course=course)
        user_ids = [user_couser.user.id for user_couser in user_cousers]
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        # 取出所有课程id
        course_ids = [user_couser.course.id for user_couser in all_user_courses]
        # 获取学过该课程的同学学过其他的课程
        relate_courses = Course.objects.filter(id__in=course_ids).order_by('-click_nums')[:5]

        all_resources = CourseResource.objects.filter(course=course)
        return render(request, 'course-video.html', {
            'course': course,
            'all_resources': all_resources,
            'relate_courses': relate_courses,
        })


class CommentsView(LoginRequiredMixin, View):
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        user_cousers = UserCourse.objects.filter(course=course)
        user_ids = [user_couser.user.id for user_couser in user_cousers]
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        # 取出所有课程id
        course_ids = [user_couser.course.id for user_couser in all_user_courses]
        # 获取学过该课程的同学学过其他的课程
        relate_courses = Course.objects.filter(id__in=course_ids).order_by('-click_nums')[:5]

        all_resources = CourseResource.objects.filter(course=course)
        all_comments = CourseComments.objects.filter(course=course).order_by('-add_time')
        return render(request, 'course-comment.html', {
            'course': course,
            'all_resources': all_resources,
            'all_comments': all_comments,
            'relate_courses': relate_courses,
        })


class AddCommentsView(View):
    """
    用户添加课程评论
    """

    def post(self, request):
        if not request.user.is_authenticated:
            # 判断用户登录状态
            return HttpResponse(json.dumps({'status': 'fail', 'msg': '用户未登录'}), content_type='application/json')

        course_id = request.POST.get('course_id', 0)
        comments = request.POST.get('comments', "")
        if int(course_id) > 0 and comments:
            course_comments = CourseComments()
            course = Course.objects.get(id=int(course_id))
            course_comments.course = course
            course_comments.comments = comments
            course_comments.user = request.user
            course_comments.save()
            return HttpResponse(json.dumps({'status': 'success', 'msg': '添加成功'}), content_type='application/json')
        else:
            return HttpResponse(json.dumps({'status': 'fail', 'msg': '添加失败'}), content_type='application/json')
