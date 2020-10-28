# Generated by Django 2.1.7 on 2019-03-16 22:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0021_auto_20190316_2220'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ignored',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.Accounts')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.Profile')),
            ],
            options={
                'db_table': 'ignored',
            },
        ),
    ]