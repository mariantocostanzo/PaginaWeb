# Generated by Django 3.2.6 on 2021-09-05 07:24

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0002_auto_20210905_0719'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logindetails',
            name='login_time',
            field=models.DateTimeField(default=datetime.datetime(2021, 9, 5, 7, 24, 11, 122720)),
        ),
        migrations.AlterField(
            model_name='partidasdetails',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2021, 9, 5, 7, 24, 11, 122976)),
        ),
    ]
