# Generated by Django 2.1.7 on 2019-03-09 23:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0006_auto_20190309_2322'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='can_hide_category',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='account_type',
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='auto_expand_chaining',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='can_hide_public_contacts',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='has_unseen_besties_media',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='highlight_reshare_disabled',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='include_direct_blacklist_status',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='is_bestie',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='is_potential_business',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='should_show_category',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='should_show_public_contacts',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='show_account_transparency_details',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
