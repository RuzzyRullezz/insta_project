# Generated by Django 2.1.7 on 2019-03-16 22:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0023_auto_20190316_2230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='external_url',
            field=models.URLField(blank=True, max_length=4096, null=True),
        ),
    ]
