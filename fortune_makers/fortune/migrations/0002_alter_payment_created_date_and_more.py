# Generated by Django 4.1.3 on 2022-11-16 07:18

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fortune', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 16, 7, 18, 2, 22017, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='withdraw',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 16, 7, 18, 2, 22221, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='withdrawreferral',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 11, 16, 7, 18, 2, 22396, tzinfo=datetime.timezone.utc)),
        ),
    ]
