# Generated by Django 2.2 on 2022-12-14 04:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles_api', '0026_test_one_off_fee_extra_hours_request'),
    ]

    operations = [
        migrations.AlterField(
            model_name='one_off_fee',
            name='servicecode',
            field=models.CharField(max_length=64),
        ),
    ]