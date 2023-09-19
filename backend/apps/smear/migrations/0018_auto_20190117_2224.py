# Generated by Django 2.1.2 on 2019-01-17 22:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smear', '0017_player_cards_in_hand'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='seat',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='team',
            field=models.CharField(blank=True, default='', max_length=1024),
        ),
    ]