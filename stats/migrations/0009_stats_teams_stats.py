# Generated by Django 4.1.4 on 2023-07-30 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0008_remove_teams_rank_team_alter_stats_sp_rank_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='stats',
            name='teams_stats',
            field=models.TextField(default=''),
        ),
    ]
