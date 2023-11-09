# Generated by Django 4.2.6 on 2023-11-09 12:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_remove_cliente_razao_social_clientepj_razao_social'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientepf',
            name='id_cliente',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.cliente'),
        ),
        migrations.AddField(
            model_name='clientepj',
            name='id_cliente',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.cliente'),
        ),
    ]
