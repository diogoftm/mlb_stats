# Generated by Django 4.0.3 on 2022-04-02 13:40

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('stats', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Games',
            new_name='Game',
        ),
    ]
