# Generated by Django 4.0 on 2022-01-13 07:03

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('wi', '0008_alter_task_updated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='created',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='description',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.BooleanField(default=False, verbose_name='Completed?'),
        ),
        migrations.AlterField(
            model_name='task',
            name='updated',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2022, 1, 13, 7, 3, 6, 185170, tzinfo=utc), null=True),
        ),
    ]
