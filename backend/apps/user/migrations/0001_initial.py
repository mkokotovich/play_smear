# Generated by Django 2.1.2 on 2019-01-09 21:05

import uuid

from django.db import migrations


computer_players = [
    {
        'first_name': 'Harry',
        'last_name': 'P',
        'username': 'mkokotovich+computer_harry@gmail.com',
    },
    {
        'first_name': 'Ron',
        'last_name': 'W',
        'username': 'mkokotovich+computer_ron@gmail.com',
    },
    {
        'first_name': 'Hermione',
        'last_name': 'G',
        'username': 'mkokotovich+computer_hermione@gmail.com',
    },
    {
        'first_name': 'Ginny',
        'last_name': 'W',
        'username': 'mkokotovich+computer_ginny@gmail.com',
    },
    {
        'first_name': 'Leif',
        'last_name': 'Ericson',
        'username': 'mkokotovich+computer_leif@gmail.com',
    },
    {
        'first_name': 'Maisie',
        'last_name': 'K',
        'username': 'mkokotovich+computer_maisie@gmail.com',
    },
    {
        'first_name': 'Barack',
        'last_name': 'O',
        'username': 'mkokotovich+computer_barack@gmail.com',
    },
    {
        'first_name': 'Michelle',
        'last_name': 'O',
        'username': 'mkokotovich+computer_michelle@gmail.com',
    },
]

def add_computer_players(apps, schema_editor):
    User = apps.get_model("auth", "User")
    for user in computer_players:
        User.objects.create(
            first_name=user['first_name'],
            last_name=user['last_name'],
            username=user['username'],
            password=str(uuid.uuid4()),
        )


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.RunPython(add_computer_players),
    ]
