# Generated by Django 2.1.7 on 2019-03-21 20:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0034_iglog'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='iglog',
            name='timestamp',
        ),
    ]