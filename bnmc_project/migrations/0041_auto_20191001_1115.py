# Generated by Django 2.0.4 on 2019-10-01 05:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bnmc_project', '0040_auto_20190914_1336'),
    ]

    operations = [
        migrations.AddField(
            model_name='userpermissionresult',
            name='exam_year',
            field=models.ManyToManyField(to='bnmc_project.ExamYear'),
        ),
        migrations.AddField(
            model_name='userpermissionresult',
            name='program',
            field=models.ManyToManyField(to='bnmc_project.Program'),
        ),
    ]