# Generated by Django 5.1.2 on 2024-10-28 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_userhealthprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='userhealthprofile',
            name='fhir_id',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
