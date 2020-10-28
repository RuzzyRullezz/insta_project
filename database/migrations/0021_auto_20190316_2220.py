# Generated by Django 2.1.7 on 2019-03-16 22:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0020_auto_20190316_2215'),
    ]

    operations = [
        migrations.RenameField(
            model_name='following',
            old_name='account',
            new_name='owner',
        ),
        migrations.RenameField(
            model_name='liked',
            old_name='account',
            new_name='owner',
        ),
        migrations.RemoveField(
            model_name='following',
            name='victim_id',
        ),
        migrations.RemoveField(
            model_name='following',
            name='victim_username',
        ),
        migrations.RemoveField(
            model_name='liked',
            name='victim_id',
        ),
        migrations.RemoveField(
            model_name='liked',
            name='victim_username',
        ),
        migrations.AddField(
            model_name='following',
            name='profile',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='database.Profile'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='liked',
            name='profile',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='database.Profile'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='following',
            name='status',
            field=models.PositiveIntegerField(choices=[(0, 'unfollow'), (1, 'follow'), (2, 'processed'), (3, 'not_found'), (4, 'requested'), (5, 'unrequested'), (6, 'block'), (7, 'unblock')]),
        ),
        migrations.AlterField(
            model_name='liked',
            name='picture_id',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterModelTable(
            name='following',
            table='followed',
        ),
    ]