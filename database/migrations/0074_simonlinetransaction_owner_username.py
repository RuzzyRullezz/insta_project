# Generated by Django 2.1.7 on 2019-07-06 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0073_simonlinetransaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='simonlinetransaction',
            name='owner_username',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
    ]