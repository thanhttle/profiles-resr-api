# Generated by Django 2.2 on 2022-10-18 01:55

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('profiles_api', '0013_remove_service_fee_list_name_lists'),
    ]

    operations = [
        migrations.AddField(
            model_name='service_fee_list',
            name='feename',
            field=jsonfield.fields.JSONField(default=dict),
        ),
    ]