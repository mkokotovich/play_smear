# Generated by Django 4.1.2 on 2022-10-21 03:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('smear', '0033_auto_20200604_0336'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='hand',
            options={'ordering': ['num']},
        ),
        migrations.AlterModelOptions(
            name='play',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='trick',
            options={'ordering': ['num']},
        ),
    ]