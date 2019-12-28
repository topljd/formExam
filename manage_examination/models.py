from django.db import models

# Create your models here.
from django.shortcuts import render
from django.utils import timezone
from django.utils.html import format_html
from mdeditor.fields import MDTextField


class Subject(models.Model):
    subject_text = models.CharField("课程名称", max_length=200)

    class Meta:
        verbose_name = '课程名称'
        verbose_name_plural = '所有课程'

    def __str__(self):
        return self.subject_text


class QuestionType(models.Model):
    question_type_text = models.CharField("题目类型", max_length=200)
    pub_date = models.DateTimeField('录入时间', default=timezone.now())

    class Meta:
        verbose_name = '题目类型'
        verbose_name_plural = '所有题目类型'

    def __str__(self):
        return self.question_type_text


class Label(models.Model):
    label_text = models.CharField(max_length=30)
    pub_date = models.DateTimeField("录入时间", auto_now=True)

    def __str__(self):
        return self.label_text

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = '标签集'


class Question(models.Model):
    question_type = models.ForeignKey(QuestionType, verbose_name="题目类型", on_delete=models.CASCADE)
    question_subject = models.ForeignKey(Subject, verbose_name="所属学科", on_delete=models.CASCADE)

    question_title = models.CharField("题目标题", max_length=1000)
    question_text = MDTextField("题目文本")
    answer_text = models.TextField("题目答案", null=True, blank=True)
    pub_date = models.DateTimeField("录入时间", auto_now=True)
    labels = models.ManyToManyField(Label, "标签", blank=True)

    class Meta:
        verbose_name = '题目'
        verbose_name_plural = '总题库'

    def __str__(self):
        return self.question_title


class Choice(models.Model):
    question = models.ForeignKey(Question, verbose_name="题目", on_delete=models.CASCADE)
    choice_text = models.CharField("选项文本", max_length=200)

    class Meta:
        verbose_name = '选项'
        verbose_name_plural = '所有选项'

    def __str__(self):
        return self.choice_text


class Paper(models.Model):
    paper_name = models.CharField("试卷标题", max_length=200)
    paper_score = models.IntegerField("试卷分数")
    paper_exam_time = models.IntegerField("考试时间")
    paper_author = models.CharField("出题人", max_length=20, blank=True)
    paper_subject = models.ForeignKey(Subject, verbose_name="考试科目", on_delete=models.CASCADE)
    paper_question = models.ManyToManyField(Question, "试卷题目")
    exam_time = models.DateTimeField("考试时间", null=True)
    pub_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.paper_name

    def get_detail(self):
        return format_html(
            '<span><a href="../paper_detail/{}">试卷内容</a></span>', self.id
        )

    def get_paper(self):
        return format_html(
            '<span><a href="../doc/{}">下载试卷</a></span>', self.id
        )

    class Meta:
        verbose_name = "试卷"
        verbose_name_plural = '试卷'
