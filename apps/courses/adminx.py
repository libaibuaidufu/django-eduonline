# coding:utf-8
__author__ = "dfk"
__date__ = "2017/12/10 10:34"

import xadmin

from .models import Course, CourseResource, Lesson, Video, BannerCourse
from organization.models import CourseOrg


class LessonInline(object):
    model = Lesson
    extra = 0


class CourseResourceInline(object):
    model = CourseResource
    extra = 0


class CourseAdmin(object):
    list_display = ['name', 'desc', 'detail', 'get_zj_nums', 'go_to', 'degree', 'learn_times', 'students', 'fav_nums',
                    'image', 'click_nums',
                    'add_time']
    search_fields = ['name', 'desc', 'detail', 'degree', 'students', 'fav_nums', 'image', 'click_nums']
    list_filter = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students', 'fav_nums', 'image', 'click_nums',
                   'add_time']
    ordering = ['-click_nums']
    list_editable = ['degree', 'desc']
    readonly_fields = ['click_nums']
    exclude = ['fav_nums']
    inlines = [LessonInline,CourseResourceInline]
    refresh_times = [3,5]
    style_fields = {"detail": "ueditor"}
    import_excel = True


    def queryset(self):
        qs = super(CourseAdmin, self).queryset()
        qs = qs.filter(is_banner=False)
        return qs

    def save_models(self):
        #在保存课程机构的时候统计课程机构的课程数
        obj = self.new_obj
        obj.save()
        if obj.course_org is not None:
            course_org = obj.course_org
            course_org.course_nums = Course.objects.filter(course_org=course_org).count()
            course_org.save()

    def post(self,request,*args,**kwargs):
        if 'excel' in request.FILES:
            pass
        return super(CourseAdmin,self).post(request,args,kwargs)


class BannerCourseAdmin(object):
    list_display = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students', 'fav_nums', 'image', 'click_nums',
                    'add_time']
    search_fields = ['name', 'desc', 'detail', 'degree', 'students', 'fav_nums', 'image', 'click_nums']
    list_filter = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students', 'fav_nums', 'image', 'click_nums',
                   'add_time']
    ordering = ['-click_nums']
    readonly_fields = ['click_nums']
    exclude = ['fav_nums']
    inlines = [LessonInline, CourseResourceInline]
    style_fields = {"detail": "ueditor"}
    import_excel = True

    def queryset(self):
        qs = super(BannerCourseAdmin, self).queryset()
        qs = qs.filter(is_banner=True)
        return qs

    def post(self,request,*args,**kwargs):
        if 'excel' in request.FILES:
            pass
        return super(BannerCourseAdmin,self).post(request,args,kwargs)



class LessonAdmin(object):
    list_display = ['course', 'name', 'add_time']
    search_fields = ['name']
    list_filter = ['course__name', 'name', 'add_time']


class VideoAdmin(object):
    list_display = ['lesson', 'name', 'add_time']
    search_fields = ['name']
    list_filter = ['lesson__name', 'name', 'add_time']


class CourseResourceAdmin(object):
    list_display = ['course', 'download', 'name', 'add_time']
    search_fields = ['download', 'name']
    list_filter = ['course__name', 'download', 'name', 'add_time']


xadmin.site.register(Course, CourseAdmin)
xadmin.site.register(BannerCourse, BannerCourseAdmin)
xadmin.site.register(Lesson, LessonAdmin)
xadmin.site.register(Video, VideoAdmin)
xadmin.site.register(CourseResource, CourseResourceAdmin)
