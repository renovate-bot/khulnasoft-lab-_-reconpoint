# Generated by Django 2.0.4 on 2019-07-31 10:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bnmc_project', '0034_auto_20190731_1622'),
    ]

    operations = [
        migrations.AddField(
            model_name='license_receive',
            name='late',
            field=models.BooleanField(default=False),
        ),
    ]