# Generated by Django 4.2.6 on 2023-11-14 12:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_client_address'),
    ]

    operations = [
        migrations.RenameField(
            model_name='card',
            old_name='brand',
            new_name='flag',
        ),
        migrations.RenameField(
            model_name='loan',
            old_name='requested_amount',
            new_name='value',
        ),
        migrations.RemoveField(
            model_name='account',
            name='type',
        ),
        migrations.RemoveField(
            model_name='card',
            name='status',
        ),
        migrations.RemoveField(
            model_name='loan',
            name='note',
        ),
    ]