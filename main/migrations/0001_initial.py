# Generated by Django 3.1.2 on 2020-10-17 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('name', models.CharField(max_length=300)),
                ('id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('reward', models.FloatField()),
                ('url', models.CharField(max_length=300)),
                ('pic', models.CharField(max_length=300)),
                ('filter', models.CharField(blank=True, max_length=300, null=True)),
                ('countries', models.CharField(max_length=1500)),
                ('categories', models.CharField(max_length=1500)),
                ('description', models.CharField(max_length=1500)),
                ('requirements', models.CharField(max_length=1500)),
                ('date', models.DateTimeField()),
            ],
        ),
    ]
