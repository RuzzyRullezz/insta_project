# Generated by Django 2.1.7 on 2019-03-12 15:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0012_auto_20190311_2252'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='posted',
            name='text',
        ),
        migrations.DeleteModel(
            name='ParsedText',
        ),
    ]
