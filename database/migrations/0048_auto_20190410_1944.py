# Generated by Django 2.1.7 on 2019-04-10 19:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0047_auto_20190408_2112'),
    ]

    operations = [
        migrations.CreateModel(
            name='Proxy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.GenericIPAddressField()),
                ('port', models.IntegerField()),
                ('username', models.CharField(blank=True, max_length=1024, null=True)),
                ('password', models.CharField(blank=True, max_length=1024, null=True)),
            ],
            options={
                'db_table': 'proxy',
            },
        ),
        migrations.RemoveField(
            model_name='accounts',
            name='proxy_ip',
        ),
        migrations.AddField(
            model_name='accounts',
            name='proxy',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='database.Proxy'),
        ),
    ]
