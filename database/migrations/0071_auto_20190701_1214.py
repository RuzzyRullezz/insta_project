# Generated by Django 2.1.7 on 2019-07-01 12:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0070_auto_20190701_1201'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='oldpost',
            name='approved',
        ),
        migrations.RemoveField(
            model_name='oldpost',
            name='posted',
        ),
        migrations.AddField(
            model_name='oldpost',
            name='text_content',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='database.TextContent'),
        ),
    ]