# Generated by Django 4.0 on 2022-01-09 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wi', '0005_rename_wi_task'),
    ]

    operations = [
        migrations.AlterField(
            model_name='area',
            name='created',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='area',
            name='name',
            field=models.CharField(max_length=25),
        ),
        migrations.AlterField(
            model_name='task',
            name='created',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='description',
            field=models.CharField(max_length=100, verbose_name='task description'),
        ),
        migrations.AlterField(
            model_name='task',
            name='priority',
            field=models.BooleanField(default=False),
        ),
    ]
