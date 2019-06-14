# Generated by Django 2.2.1 on 2019-06-03 21:47

from django.db import migrations, models
import django.db.models.deletion
import swingtime.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', models.TextField(verbose_name='note')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('object_id', models.PositiveIntegerField(verbose_name='object id')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType', verbose_name='content type')),
            ],
            options={
                'verbose_name': 'note',
                'verbose_name_plural': 'notes',
            },
        ),
        migrations.CreateModel(
            name='EventType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sib_order', models.PositiveIntegerField(null=True)),
                ('label', models.CharField(max_length=50, unique=True, verbose_name='label')),
                ('parent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children_set', to='swingtime.EventType')),
            ],
            options={
                'verbose_name': 'event type',
                'verbose_name_plural': 'event types',
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=32, verbose_name='title')),
                ('recurrences', swingtime.fields.RecurrenceField(blank=True, default=None, null=True)),
                ('event_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='swingtime.EventType', verbose_name='event type')),
            ],
            options={
                'verbose_name': 'event',
                'verbose_name_plural': 'events',
                'ordering': ('title',),
            },
        ),
    ]
