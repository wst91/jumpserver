# Generated by Django 3.1 on 2021-01-07 07:47

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0008_auto_20210104_0435'),
    ]

    operations = [
        migrations.CreateModel(
            name='RemoteAppType',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('created_by', models.CharField(blank=True, max_length=32, null=True, verbose_name='Created by')),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Date created')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='Date updated')),
                ('name', models.CharField(max_length=128)),
                ('display_name', models.CharField(max_length=128)),
                ('description', models.TextField()),
                ('author', models.CharField(max_length=128)),
                ('company', models.CharField(blank=True, max_length=128, null=True)),
                ('license', models.CharField(blank=True, max_length=128, null=True)),
                ('tags', models.JSONField()),
                ('params', models.JSONField()),
                ('i18n', models.JSONField()),
            ],
            options={
                'abstract': False,
            },
        ),
    ]