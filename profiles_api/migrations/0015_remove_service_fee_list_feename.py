# Generated by Django 2.2 on 2022-10-19 00:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles_api', '0014_service_fee_list_feename'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='service_fee_list',
            name='feename',
        ),
    ]
