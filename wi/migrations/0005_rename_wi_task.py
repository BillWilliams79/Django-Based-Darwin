# Generated by Django 4.0 on 2022-01-08 10:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wi', '0004_rename_tasker_wi'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='wi',
            new_name='task',
        ),
    ]
