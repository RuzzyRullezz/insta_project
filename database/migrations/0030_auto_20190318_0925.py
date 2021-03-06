# Generated by Django 2.1.7 on 2019-03-18 09:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0029_auto_20190317_2137'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='following',
            unique_together={('profile', 'owner')},
        ),
        migrations.AlterUniqueTogether(
            name='liked',
            unique_together={('profile', 'owner', 'picture_id')},
        ),
    ]
