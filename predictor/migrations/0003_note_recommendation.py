# Generated by Django 5.1 on 2024-08-16 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('predictor', '0002_alter_prediction_prediction_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='recommendation',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
