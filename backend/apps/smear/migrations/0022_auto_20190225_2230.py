# Generated by Django 2.1.2 on 2019-02-25 22:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('smear', '0021_auto_20190213_1459'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bid',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('bid', models.IntegerField(blank=True, default=0)),
            ],
        ),
        migrations.RemoveField(
            model_name='hand',
            name='deleted_at',
        ),
        migrations.AddField(
            model_name='hand',
            name='bidder',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='hands_was_bidder', to='smear.Player'),
        ),
        migrations.AddField(
            model_name='hand',
            name='dealer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='smear.Player'),
        ),
        migrations.AddField(
            model_name='hand',
            name='trump',
            field=models.CharField(blank=True, default='', max_length=16),
        ),
        migrations.AddField(
            model_name='player',
            name='plays_after',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='plays_before', to='smear.Player'),
        ),
        migrations.AddField(
            model_name='bid',
            name='hand',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bids', to='smear.Hand'),
        ),
        migrations.AddField(
            model_name='bid',
            name='player',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bids', to='smear.Player'),
        ),
        migrations.AddField(
            model_name='hand',
            name='high_bid',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='hand_with_high_bid', to='smear.Bid'),
        ),
    ]