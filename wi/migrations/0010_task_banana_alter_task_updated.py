# Generated by Django 4.0 on 2022-01-13 07:35

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('wi', '0009_alter_task_created_alter_task_description_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='banana',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='task',
            name='updated',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2022, 1, 13, 7, 35, 25, 444151, tzinfo=utc), null=True),
        ),
    ]
