# Generated by Django 4.2.6 on 2023-11-29 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_alter_client_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='approval_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='status',
            field=models.CharField(choices=[('In Approval', 'In Approval'), ('Approved', 'Approved')], default='In Approval', max_length=20),
        ),
    ]