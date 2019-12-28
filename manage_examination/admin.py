from django.contrib import admin

# Register your models here.
from django.db import models

from manage_examination.models import Choice, Question, QuestionType, Subject, Paper, Label


class QuestionTypeAdmin(admin.ModelAdmin):
    fieldsets = [
        ('类型名称', {'fields': ['question_type_text']}),
    ]
    list_display = ["question_type_text", "pub_date"]


class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 4
    max_num = 4


class ChoiceAdmin(admin.ModelAdmin):
    fieldsets = [
        ('选项文本', {'fields': ['choice_text']}),
        ('选项题目', {'fields': ['question']})
    ]
    list_display = ("choice_text", "question")
    search_fields = ['choice_text']

def remove_duplicated_records(model, fields):
    """
    Removes records from `model` duplicated on `fields`
    while leaving the most recent one (biggest `id`).
    """
    duplicates = (model.objects.values(*fields)
                               .order_by()
                               .annotate(max_id=models.Max('id'),
                                         count_id=models.Count('id'))
                               .filter(count_id__gt=1))

    for duplicate in duplicates:
        (model.objects.filter(**{x: duplicate[x] for x in fields})
                      .exclude(id=duplicate['max_id'])
                      .delete())



class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        ('题目类型', {'fields': ['question_type']}),
        ('题目标题', {'fields': ['question_title']}),
        ('所属科目', {'fields': ['question_subject']}),
        ('题目文本', {'fields': ['question_text']}),
        ('题目答案', {'fields': ['answer_text']}),
        ('题目标签', {'fields': ['labels']})
    ]
    inlines = [ChoiceInline]
    list_display = ('question_title', 'pub_date', 'question_type')
    list_filter = ['pub_date']
    search_fields = ['question_text']
    filter_horizontal = ('labels',)

    def check_unique(self, request, queryset):
        remove_duplicated_records(Question, ['question_text', 'question_subject_id'])
        pass

    check_unique.short_description = "查重"
    actions = ("check_unique",)

    def __str__(self):
        return "题目"


class QuestionInline(admin.TabularInline):
    model = Question


@admin.register(Paper)
class PaperAdmin(admin.ModelAdmin):
    fieldsets = [
        ("试卷名称", {'fields': ['paper_name']}),
        ("出题人", {'fields': ['paper_author']}),
        ("考试时间", {'fields': ['exam_time']}),
        ("试卷属性", {"fields": ['paper_subject', 'paper_score', 'paper_exam_time']}),
        ("试卷内容", {"fields": ['paper_question']})
        # ("考试日期"),{"fileds":['']}
    ]
    filter_horizontal = ('paper_question',)

    list_display = ('paper_name', 'paper_subject', 'exam_time', 'get_detail', 'get_paper')
    search_fields = ['paper_name', 'paper_subject']
    list_display_links = ("paper_name",)


admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice, ChoiceAdmin)
admin.site.register(QuestionType, QuestionTypeAdmin)
admin.site.register(Subject)
admin.site.register(Label)
admin.site.site_title = "试题管理系统"
admin.site.site_header = "试题管理系统"
admin.site.index_title = "试题管理系统"
