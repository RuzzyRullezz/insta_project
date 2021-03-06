# Generated by Django 2.1.7 on 2019-04-03 20:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0044_auto_20190324_0829'),
    ]

    operations = [
        migrations.AlterField(
            model_name='following',
            name='status',
            field=models.PositiveIntegerField(choices=[(0, 'unfollow'), (1, 'follow'), (2, 'processed'), (3, 'not_found'), (4, 'requested'), (5, 'unrequested'), (6, 'block'), (7, 'unblock'), (8, 'user_deleted')], db_index=True),
        ),
    ]
