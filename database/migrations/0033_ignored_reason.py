# Generated by Django 2.1.7 on 2019-03-20 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0032_auto_20190318_2056'),
    ]

    operations = [
        migrations.AddField(
            model_name='ignored',
            name='reason',
            field=models.TextField(blank=True, null=True),
        ),
    ]
