# Generated by Django 5.1.3 on 2024-11-12 04:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_user_wallet_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='national_id',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
    ]
