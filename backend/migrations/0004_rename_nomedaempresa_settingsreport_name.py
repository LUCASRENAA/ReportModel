# Generated by Django 4.2.11 on 2024-06-16 14:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0003_settingsreport'),
    ]

    operations = [
        migrations.RenameField(
            model_name='settingsreport',
            old_name='nomedaempresa',
            new_name='name',
        ),
    ]
