# Generated by Django 5.1.3 on 2024-11-12 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agriculture', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='agriculturedata',
            name='bananas',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='agriculturedata',
            name='oranges',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='agriculturedata',
            name='plantains',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='agriculturedata',
            name='rice',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
