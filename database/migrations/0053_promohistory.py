# Generated by Django 2.1.7 on 2019-04-15 19:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0052_auto_20190411_1915'),
    ]

    operations = [
        migrations.CreateModel(
            name='PromoHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateTimeField(auto_now_add=True)),
                ('end', models.DateTimeField(blank=True, null=True)),
                ('promo_type', models.PositiveIntegerField(choices=[(1, 1), (2, 2), (3, 3)])),
                ('success', models.NullBooleanField()),
                ('traceback', models.TextField(blank=True, null=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.Accounts')),
            ],
            options={
                'db_table': 'promo_history',
            },
        ),
    ]
