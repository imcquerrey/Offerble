# Generated by Django 3.0.6 on 2020-10-20 00:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20201019_2359'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='cookie',
            field=models.CharField(default='nope', max_length=300),
        ),
    ]