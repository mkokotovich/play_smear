# Generated by Django 2.1.2 on 2018-12-21 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smear', '0005_game_passcode'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='passcode_required',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]