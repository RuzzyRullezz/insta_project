# Generated by Django 2.1.7 on 2019-06-02 07:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0064_externalproxy'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='promo_type',
            field=models.PositiveIntegerField(blank=True, choices=[(1, 1), (2, 2), (3, 3)], db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='promohistory',
            name='promo_type',
            field=models.PositiveIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4)]),
        ),
    ]
