from django import forms

from manage_examination.models import Subject, QuestionType


class UploadFileForm(forms.Form):
    subject = forms.ChoiceField(label="科目", choices=Subject.objects.values_list("id", "subject_text"))
    question_type = forms.ChoiceField(label="题目类型",
                                      choices=QuestionType.objects.values_list("id", "question_type_text"))
    file = forms.FileField(label="文件")
