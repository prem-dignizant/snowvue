# Generated by Django 5.1.3 on 2024-12-20 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0011_delete_userhealthprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='ssn',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
    ]
