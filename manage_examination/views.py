import os
import re
from urllib import request

from django.db.models import Q
from django.http import HttpResponse, FileResponse, JsonResponse
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.utils import timezone
from django.views import generic
from docxtpl import DocxTemplate, InlineImage

from formExam import settings
from manage_examination.forms import UploadFileForm
from manage_examination.models import Subject, Paper, QuestionType, Label, Question
from package import handle_upload_file, latex2img


def create_paper(request):
    # post请求提交表单
    if request.method == "POST":
        # 获取表单中的学科
        subject = request.POST['subject']
        # 获取表单中的分数
        score = request.POST['score']
        # 获取表单中的试卷名称
        name = request.POST['name']
        # 获取表单中的考试时间
        time = request.POST['time']
        # 获取选中题目的各个类型
        question_type = request.POST.getlist('check_box_list')
        # 题目-数量对照表 用于存储需要添加题目类型和所对应的数量
        question_num = {}
        for i in question_type:
            question_num[i] = int(request.POST["%s_num" % i])
        # 获取所选中的标签
        labels = request.POST.getlist('states')
        # 新建一个试卷
        new_paper = Paper()
        # 根据获取的信息填写新试卷的信息
        new_paper.paper_name = name
        new_paper.paper_score = score
        new_paper.paper_subject_id = subject
        new_paper.paper_exam_time = int(time)
        # 保存新试卷 否则无法对试卷的题目进行添加 因为需要试卷-题目关联表中的试卷id
        new_paper.save()
        # 遍历题目-数量表
        for type_id, num in list(question_num.items()):
            # 通过所选科目和题目类型、标签从数据库中随机查找相应数量的题目
            filtered_set = Question.objects.filter(question_subject_id=subject, question_type_id=type_id,
                                                   labels__in=labels).order_by("?")[
                           :int(num)]
            for question_id in filtered_set.values_list("id"):
                # 添加题目
                new_paper.paper_question.add(question_id[0])
                # 题目数量-1
                question_num[type_id] -= 1
                # 若已取够题目就把题目类型从题目-数量表中删除
                if question_num[type_id] == 0:
                    question_num.pop(type_id)
        # 如果题目-数量表还存在元素 则表示按标签取题目并未取够
        if question_num:
            # 获取已添加题目的id
            added_id = new_paper.paper_question.values_list("id")
            # 逐一处理未添加够的题目
            for type_id, num in question_num.items():
                # 通过学科、题目类型选择一定数量的未添加题目
                filtered_set = Question.objects.filter(
                    Q(question_subject_id=subject) & Q(question_type_id=type_id) & ~Q(id__in=added_id)).order_by("?")[
                               :int(num)]
                # 添加题目进入试卷
                for question_id in filtered_set.values_list("id"):
                    new_paper.paper_question.add(question_id[0])
        # 成功提示
        return HttpResponse("<script>alert('success')</script>")
    # get请求读取页面
    else:
        # 获得所有学科
        subjects = Subject.objects.all()
        # 获得所有标签
        labels = Label.objects.all()
        # 获得所有题目类型
        question_types = QuestionType.objects.all()
        # 填充模板并定向到模板
        return render(request, 'manage_examination/create_paper.html', {
            'subjects': subjects,
            'labels': labels,
            'question_types': question_types,
        })


def upload_file(request):
    # post请求处理表单
    if request.method == 'POST':
        # 实例化UploadFileForm类接受表单信息
        form = UploadFileForm(request.POST, request.FILES)
        # 验证表单是否合理（文件是否上传）
        if form.is_valid():
            # 上传文本文件
            handle_upload_file(request.FILES['file'], request)
            # 提示成功
            return HttpResponse("<script>alert('添加成功')</script>")
        # 若表单不合理则返回
        else:
            print(form.errors)
    # get请求页面
    else:
        # 实例化空表单
        form = UploadFileForm()
    # 把空表单到前台进行渲染
    return render(request, 'manage_examination/upload.html', {'form': form})


# 下载试卷
def get_document(request, paper_id):
    # 根据id获取试卷
    paper = Paper.objects.get(id=paper_id)
    # 填充考试日期
    exam_time = paper.exam_time
    # 判断学期
    # 根据考试日期判断学期
    if 3 <= exam_time.month <= 7:
        term = 3
    elif 7 < exam_time.month < 10:
        term = 1
    else:
        term = 2
    if term == 1 or 2:
        grade = "%s-%s" % (str(exam_time.year), str(exam_time.year + 1))
    else:
        grade = "%s-%s" % (str(exam_time.year - 1), str(exam_time.year))
    # 读取word文档模板
    doc = DocxTemplate("templates/template.docx")
    # 问题填充列表 把问题填充到富文本占位符中
    question_context = {}
    # 公式填充列表
    latex_context = {}
    # 填充富文本占位符
    rt = fill_richtext(paper, question_context, latex_context, doc)
    # 基本信息填充列表
    context = {
        'title': paper.paper_name,
        'score': paper.paper_score,
        'term': str(term),
        'grade': grade,
        'subject': paper.paper_subject,
        'author': paper.paper_author,
        'page_count': '2',
        'question_count': '2',
        'rt': rt,
    }
    # 渲染基本信息
    doc.render(context)
    # 渲染题目
    doc.render(question_context)
    # 渲染公式
    doc.render(latex_context)
    # 输出文件目录
    docx_file = "templates/generated_doc.docx"
    # 文件输出
    doc.save(docx_file)
    # 打开文件流
    file = open('templates/generated_doc.docx', 'rb')
    # 返回文件流供用户下载
    response = FileResponse(file, as_attachment=True, filename="%s.docx" % paper.paper_name)

    return response


# 填充富文本占位符
def fill_richtext(paper: Paper, question_content, latex_context, tpl):
    """
    填充题目富文本
    :param paper:试卷
    :param question_content:题目占位符表
    :param latex_context:公式文本占位符
    :param tpl:填充的模板
    """
    import docxtpl
    # 中文项目符号
    CHINESE_INDEX_LIST = ('一、', '二、', '三、', '四、', '五、', '六、', '七、')
    # 选项项目符号
    CHOICE_INDEX_LIST = ('A.', 'B.', 'C.', 'D.', 'E.', 'F.', 'G.')
    # 创建富文本
    rich_text = docxtpl.RichText()
    # 获取试卷题目类型id
    types = paper.paper_question.values("question_type").distinct()
    # 公式序号
    latex_index = 0
    # 遍历类型 以便于顺序填充各个类型的题目
    for type_index, type_dict in enumerate(types):
        # 根据题目类型id获得题目类型的文本 如：选择题
        type_text = QuestionType.objects.get(id=type_dict['question_type']).serializable_value("question_type_text")
        # 为题目标题添加描述 如：三、填空题
        rich_text.add("%s%s。\n" % (
            CHINESE_INDEX_LIST[type_index],
            type_text), size=24, bold=True)
        # 该类型题目的序号
        question_index = 0
        # 遍历当前试卷的指定题目类型下的所有题目
        for question in paper.paper_question.filter(question_type=type_dict['question_type']):
            # 公式的正则表达模式 以匹配latex公式中的$$$$ 符号
            reg = re.compile(r"\$\$(.*?)\$\$")
            # 题目文本
            question_text = question.question_text
            # 找到题目文本中的公式文本
            latexes = re.findall(reg, question.question_text)
            # 若当前题目存在公式
            if latexes:
                # 遍历各个公式
                for latex in latexes:
                    # 把\转义为%5C 在url中不可以存在\
                    latex_text = latex.replace('\\', "%5C")
                    # 把latex公式转化为png图片
                    latex2img("$$" + latex + "$$", "static/temp_img/%s" % latex_text)
                    # 根据题目文本把题目文本中的公式文本改造为公式占位符
                    question_text = question_text.replace("$$" + latex + "$$", "{{ latex_%s }}" % str(latex_index))

                    # 使用指定图片替换公式占位符
                    latex_context["latex_%s" % str(latex_index)] = InlineImage(tpl,
                                                                               "static/temp_img/%s.png" % latex_text)
                    # 公式序号+1
                    latex_index += 1
                # 把题目占位符加入到富文本中
                rich_text.add(
                    "%s.{{question%s_%s}}" % (str(question_index + 1), type_dict['question_type'], str(question_index)),
                    size=24)
            # 若该题目不存在公式
            else:
                # 直接把题目添加到富文本中
                rich_text.add(
                    "%s.{{question%s_%s}}" % (str(question_index + 1), type_dict['question_type'], str(question_index)),
                    size=24)
            # 使用处理好的题目文本填充到题目占位符
            question_content["question%s_%s" % (type_dict['question_type'], str(question_index))] = question_text
            # 为选择题添加括号
            if type_text == "选择题":
                rich_text.add("(    )\n")
                # 选项序号
                choice_index = 0
                # 填充各个选项
                for choice in question.choice_set.get_queryset():
                    rich_text.add("%s{{question%s_%s_%s}}    " % (
                        CHOICE_INDEX_LIST[choice_index], type_dict['question_type'], str(question_index),
                        str(choice_index)),
                                  size=24)
                    question_content["question%s_%s_%s" % (
                        type_dict['question_type'], str(question_index), str(choice_index))] = choice.choice_text
                    choice_index += 1
                rich_text.add("\n")
            # 为判断题添加括号
            elif type_text == "判断题":
                rich_text.add("(    )\n", size=24)
            # 为题目添加书写空间
            elif type_text == ("计算题" or "主观题" or "简答题"):
                rich_text.add(6 * "\n")
            else:
                rich_text.add("\n")
            # 题目序号+1
            question_index += 1

    return rich_text


# 试卷详情视图
class PaperDetailView(generic.DetailView):
    # 获取的模型名称
    model = Paper

    # 获得填充文本
    def get_context_data(self, **kwargs):
        # 使用父方法获取填充文本
        content = super().get_context_data(**kwargs)
        # 获取当前试卷
        obj = super().get_object()
        # 获取试卷所有题目的类型
        types = obj.paper_question.values("question_type").distinct()
        # 添加试卷填充类型
        content['types'] = QuestionType.objects.filter(id__in=types)

        return content
