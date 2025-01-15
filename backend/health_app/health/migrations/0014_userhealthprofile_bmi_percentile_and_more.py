# Generated by Django 5.1.4 on 2025-01-15 06:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('health', '0013_remove_contractrecipient_data_file_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userhealthprofile',
            name='bmi_percentile',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='userhealthprofile',
            name='body_temperature',
            field=models.FloatField(blank=True, default=36.8, null=True),
        ),
        migrations.AddField(
            model_name='userhealthprofile',
            name='heart_rate',
            field=models.FloatField(blank=True, default=75, null=True),
        ),
        migrations.AddField(
            model_name='userhealthprofile',
            name='pulse_oximetry',
            field=models.FloatField(blank=True, default=98, null=True),
        ),
        migrations.AddField(
            model_name='userhealthprofile',
            name='respiratory_rate',
            field=models.IntegerField(blank=True, default=16, null=True),
        ),
    ]
