# Generated by Django 2.1.7 on 2019-03-09 23:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0005_auto_20190309_2322'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='is_business',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
