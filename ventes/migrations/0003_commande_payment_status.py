# Generated by Django 2.1.7 on 2019-03-16 13:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ventes', '0002_commandemeeting_qrcode'),
    ]

    operations = [
        migrations.AddField(
            model_name='commande',
            name='payment_status',
            field=models.BooleanField(default=False),
        ),
    ]