# Generated by Django 4.0 on 2022-02-18 04:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wi', '0024_alter_area_created_by_alter_area_domain_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='area',
            options={'ordering': ('order',)},
        ),
        migrations.AddField(
            model_name='area',
            name='order',
            field=models.PositiveIntegerField(db_index=True, default=1, editable=False, verbose_name='order'),
            preserve_default=False,
        ),
    ]
