# Generated by Django 2.1.7 on 2019-04-28 05:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0057_promohistory_process_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='parsinghistory',
            name='process_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]