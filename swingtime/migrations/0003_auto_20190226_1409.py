# Generated by Django 2.1.7 on 2019-02-26 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('swingtime', '0002_auto_20190226_1347'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='eventtype',
            name='abbr',
        ),
        migrations.AlterField(
            model_name='eventtype',
            name='label',
            field=models.CharField(max_length=50, unique=True, verbose_name='label'),
        ),
    ]
