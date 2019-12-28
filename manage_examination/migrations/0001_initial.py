# Generated by Django 2.2.4 on 2019-11-04 11:09

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc
import mdeditor.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='QuestionType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_type_text', models.CharField(max_length=200, verbose_name='题目类型')),
                ('pub_date', models.DateTimeField(default=datetime.datetime(2019, 11, 4, 11, 9, 11, 839469, tzinfo=utc), verbose_name='录入时间')),
            ],
            options={
                'verbose_name': '题目类型',
                'verbose_name_plural': '所有题目类型',
            },
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject_text', models.CharField(max_length=200, verbose_name='课程名称')),
            ],
            options={
                'verbose_name': '课程名称',
                'verbose_name_plural': '所有课程',
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_title', models.CharField(max_length=1000, unique=True, verbose_name='题目标题')),
                ('question_text', mdeditor.fields.MDTextField(verbose_name='题目文本')),
                ('answer_text', models.TextField(blank=True, null=True, verbose_name='题目答案')),
                ('pub_date', models.DateTimeField(auto_now=True, verbose_name='录入时间')),
                ('question_subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manage_examination.Subject', verbose_name='所属学科')),
                ('question_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manage_examination.QuestionType', verbose_name='题目类型')),
            ],
            options={
                'verbose_name': '题目',
                'verbose_name_plural': '总题库',
            },
        ),
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('choice_text', models.CharField(max_length=200, verbose_name='选项文本')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manage_examination.Question', verbose_name='题目')),
            ],
            options={
                'verbose_name': '选项',
                'verbose_name_plural': '所有选项',
            },
        ),
    ]