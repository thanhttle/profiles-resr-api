# Generated by Django 2.2 on 2022-12-29 00:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles_api', '0034_auto_20221228_2004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service_fee_list',
            name='from_date',
            field=models.DateField(blank=True),
        ),
        migrations.AlterField(
            model_name='service_fee_list',
            name='to_date',
            field=models.DateField(blank=True),
        ),
    ]
