# Generated by Django 2.1.7 on 2019-03-22 20:45

from django.db import migrations


def set_passed(apps, schema_editor):
    Profile = apps.get_model('database', 'Profile')
    Profile.objects.filter(
        passed=False,
        following__isnull=False,
    ).update(
        promo_type=1,
        passed=True
    )
    Profile.objects.filter(
        passed=False,
        liked__isnull=False,
    ).update(
        promo_type=2,
        passed=True
    )
    Profile.objects.filter(
        passed=False,
        ignored__isnull=False,
    ).update(
        passed=True
    )

class Migration(migrations.Migration):

    dependencies = [
        ('database', '0041_profile_passed'),
    ]

    operations = [
        migrations.RunPython(set_passed),
    ]