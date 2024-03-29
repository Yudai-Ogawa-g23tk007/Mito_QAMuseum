# Generated by Django 4.2 on 2023-06-26 01:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('QAmuseum', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userpath',
            name='count',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='userpath',
            name='browse',
            field=models.FloatField(choices=[(2.0, '速い'), (1.5, 'やや速い'), (1.0, '普通'), (0.75, 'やや遅い'), (0.5, '遅い')], default=1.0),
        ),
        migrations.AlterField(
            model_name='userpath',
            name='museumname',
            field=models.CharField(default='大村智記念学術館', max_length=100),
        ),
        migrations.AlterField(
            model_name='userpath',
            name='next_spot',
            field=models.IntegerField(default=7),
        ),
        migrations.AlterField(
            model_name='userpath',
            name='speed',
            field=models.IntegerField(choices=[(100, '速い'), (80, '普通'), (60, '遅い')], default=80),
        ),
    ]
