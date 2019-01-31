# Generated by Django 2.1.2 on 2019-01-29 17:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('smear', '0018_auto_20190117_2224'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='team',
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1024)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teams', to='smear.Game')),
            ],
        ),
        migrations.AddField(
            model_name='player',
            name='team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='players', to='smear.Team'),
        ),
    ]
