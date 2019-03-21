# Generated by Django 2.1.7 on 2019-03-21 09:38

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0003_auto_20190317_1510'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meeting',
            name='price',
            field=models.DecimalField(decimal_places=2, default=Decimal('15'), max_digits=5, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(150)]),
        ),
    ]
