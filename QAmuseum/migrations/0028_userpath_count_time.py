# Generated by Django 4.2 on 2023-08-21 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('QAmuseum', '0027_userpath_calc_bool'),
    ]

    operations = [
        migrations.AddField(
            model_name='userpath',
            name='count_time',
            field=models.FloatField(default=0),
        ),
    ]
