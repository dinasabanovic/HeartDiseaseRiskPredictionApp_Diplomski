# Generated by Django 5.1 on 2024-08-14 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('predictor', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prediction',
            name='prediction_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
