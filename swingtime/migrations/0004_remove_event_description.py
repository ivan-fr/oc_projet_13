# Generated by Django 2.1.7 on 2019-02-26 16:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('swingtime', '0003_auto_20190226_1409'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='description',
        ),
    ]
