# Generated by Django 5.1.4 on 2024-12-30 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_user_stripe_id_user_subscription_expiry_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='ssn',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
    ]
