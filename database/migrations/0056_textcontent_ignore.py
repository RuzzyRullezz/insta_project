# Generated by Django 2.1.7 on 2019-04-23 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0055_auto_20190422_1946'),
    ]

    operations = [
        migrations.AddField(
            model_name='textcontent',
            name='ignore',
            field=models.BooleanField(default=False),
        ),
    ]