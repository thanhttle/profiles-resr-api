# Generated by Django 2.2 on 2022-11-08 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles_api', '0018_test_one_off_fee_subscription_schedule_details'),
    ]

    operations = [
        migrations.AddField(
            model_name='test_one_off_fee',
            name='urgentbooking',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='test_one_off_fee',
            name='bookdate',
            field=models.DateField(blank=True),
        ),
        migrations.AlterField(
            model_name='test_one_off_fee',
            name='starttime',
            field=models.TimeField(blank=True),
        ),
    ]