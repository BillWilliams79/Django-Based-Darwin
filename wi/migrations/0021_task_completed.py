# Generated by Django 4.0 on 2022-02-12 19:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wi', '0020_domain_retain_done_tasks'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='completed',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
