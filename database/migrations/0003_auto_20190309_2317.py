# Generated by Django 2.1.7 on 2019-03-09 23:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0002_auto_20190309_2316'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='mutual_followers_count',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
