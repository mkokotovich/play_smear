# Generated by Django 2.1.2 on 2019-01-16 14:39

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smear', '0016_game_players'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='cards_in_hand',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=2), default=list, size=None),
        ),
    ]