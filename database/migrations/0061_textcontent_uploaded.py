# Generated by Django 2.1.7 on 2019-05-11 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0060_auto_20190428_1334'),
    ]

    operations = [
        migrations.AddField(
            model_name='textcontent',
            name='uploaded',
            field=models.NullBooleanField(),
        ),
    ]