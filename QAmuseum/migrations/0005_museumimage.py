# Generated by Django 4.2 on 2023-07-30 17:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('QAmuseum', '0004_rename_explain_omuramuseum_exp'),
    ]

    operations = [
        migrations.CreateModel(
            name='MuseumImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='media_local')),
                ('name', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='QAmuseum.omuramuseum')),
            ],
        ),
    ]
