# Generated by Django 5.1.3 on 2024-12-17 11:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0003_remove_notification_data_points_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='expiry_time',
        ),
    ]
