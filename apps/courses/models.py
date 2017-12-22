# coding:utf-8
from datetime import datetime
from DjangoUeditor.models import UEditorField

from django.db import models
from organization.models import CourseOrg, Teacher


# Create your models here.


class Course(models.Model):
    course_org = models.ForeignKey(CourseOrg, on_delete=models.CASCADE, null=True, blank=True, verbose_name='课程机构')
    name = models.CharField(max_length=50, verbose_name=u"课程名")
    desc = models.CharField(max_length=300, verbose_name=u"课程描述")
    detail = UEditorField(verbose_name='课程详情', width=600, height=300, imagePath="courses/ueditor/",
                          filePath="courses/ueditor/",
                          default='')
    is_banner = models.BooleanField(default=False, verbose_name="是否轮播")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name='讲师', null=True, blank=True)
    degree = models.CharField(verbose_name='难度', max_length=2, choices=(("cj", "初级"), ("zj", "中级"), ("gj", "高级")))
    learn_times = models.IntegerField(default=0, verbose_name=u"学习时长(分钟数)")
    students = models.IntegerField(default=0, verbose_name=u"学习人数")
    fav_nums = models.IntegerField(default=0, verbose_name=u"收藏人数")
    image = models.ImageField(null=True, blank=True, upload_to="courses/%Y/%m", verbose_name=u"封面图", max_length=100)
    click_nums = models.IntegerField(default=0, verbose_name=u"点击数")
    category = models.CharField(max_length=20, verbose_name="课程类别", default="后端开发")
    tag = models.CharField(default="", verbose_name="课程标签", max_length=20)
    youneed_konw = models.CharField(default="", verbose_name="课程需知", max_length=300)
    teacher_tell = models.CharField(default="", max_length=300, verbose_name='老师告诉你')
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"课程"
        verbose_name_plural = verbose_name

    def get_zj_nums(self):
        # 获取章节数
        return self.lesson_set.all().count()

    get_zj_nums.short_description = '章节数'

    def go_to(self):
        from django.utils.safestring import mark_safe
        return mark_safe("<a href='http://www.baidu.com'>跳转</a>")

    go_to.short_description = '跳转'

    def get_learn_users(self):
        # 获取学习用户
        return self.usercourse_set.all()[:5]

    def get_teacher_nums(self):
        # 获取课程机构的教师数量
        return self.course_org.teacher_set.all().count()

    def get_course_lesson(self):
        # 获取课程所有章节
        return self.lesson_set.all()

    def __str__(self):
        return self.name


class BannerCourse(Course):
    class Meta:
        verbose_name = "轮播课程"
        verbose_name_plural = verbose_name
        proxy = True


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="课程名")
    name = models.CharField(max_length=100, verbose_name=u"章节名")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = "章节"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def get_lesson_video(self):
        return self.video_set.all()


class Video(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, verbose_name="章节")
    learn_times = models.IntegerField(default=0, verbose_name=u"学习时长(分钟数)")
    name = models.CharField(max_length=100, verbose_name=u"视频名")
    url = models.CharField(max_length=200, verbose_name="访问地址", default="")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = "视频"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class CourseResource(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="课程名")
    name = models.CharField(max_length=100, verbose_name=u"名称")
    download = models.FileField(max_length=100, upload_to="courses/resource/%Y/%m", verbose_name="资源")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = "课程资源"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
