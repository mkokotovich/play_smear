# Generated by Django 4.1.2 on 2022-11-04 02:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smear', '0035_hand_players_out_of_suits'),
    ]

    operations = [
        migrations.AddField(
            model_name='hand',
            name='finished',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]