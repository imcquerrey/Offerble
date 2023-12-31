# Generated by Django 3.0.6 on 2020-10-19 23:41

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=300)),
                ('password', models.CharField(max_length=1000)),
                ('unique', models.CharField(max_length=300)),
                ('balance', models.FloatField(default=0)),
                ('clicks', models.IntegerField(default=0)),
                ('conversions', models.IntegerField(default=0)),
                ('rpc', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Client_InvalidPostBack',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(max_length=300)),
                ('offerwall', models.CharField(max_length=300)),
                ('unique', models.CharField(max_length=300)),
                ('playerid', models.CharField(max_length=300)),
                ('client_wall', models.IntegerField()),
                ('reward_earned', models.FloatField()),
                ('reward_paid', models.FloatField()),
                ('offer_name', models.CharField(max_length=300)),
                ('offer_id', models.CharField(max_length=300)),
                ('transid', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Client_ValidPostBack',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('offerwall', models.CharField(max_length=300)),
                ('unique', models.CharField(max_length=300)),
                ('playerid', models.CharField(max_length=300)),
                ('client_wall', models.IntegerField()),
                ('reward_earned', models.FloatField()),
                ('reward_paid', models.FloatField()),
                ('offer_name', models.CharField(max_length=300)),
                ('offer_id', models.CharField(max_length=300)),
                ('transid', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique', models.CharField(max_length=300)),
                ('status', models.CharField(default='Pending', max_length=300)),
                ('method', models.CharField(max_length=300)),
                ('address', models.CharField(max_length=300)),
                ('email', models.CharField(max_length=300)),
                ('amount', models.FloatField(default=0)),
                ('international', models.BooleanField(blank=True, null=True)),
                ('firstname', models.CharField(blank=True, max_length=300, null=True)),
                ('lastname', models.CharField(blank=True, max_length=300, null=True)),
                ('stree_addr', models.CharField(blank=True, max_length=300, null=True)),
                ('state', models.CharField(blank=True, max_length=300, null=True)),
                ('city', models.CharField(blank=True, max_length=300, null=True)),
                ('zipcode', models.CharField(blank=True, max_length=300, null=True)),
                ('routing', models.CharField(blank=True, max_length=300, null=True)),
                ('acc_number', models.CharField(blank=True, max_length=300, null=True)),
                ('country', models.CharField(blank=True, max_length=300, null=True)),
                ('biz_type', models.CharField(blank=True, max_length=300, null=True)),
                ('bank_id', models.CharField(blank=True, max_length=300, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Offerwall',
            fields=[
                ('unique', models.CharField(max_length=300)),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('created', models.DateField(default=django.utils.timezone.now)),
                ('postback', models.CharField(max_length=400)),
                ('secret', models.CharField(max_length=35)),
                ('currency_name', models.CharField(max_length=30)),
                ('currencys_name', models.CharField(max_length=30)),
                ('currency_abr', models.CharField(max_length=30)),
                ('currency_mult', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Stat_10',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique', models.CharField(max_length=300)),
                ('day', models.IntegerField(default=0)),
                ('users', models.IntegerField(default=0)),
                ('earnings', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Stat_24',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique', models.CharField(max_length=300)),
                ('hour', models.IntegerField(default=0)),
                ('users', models.IntegerField(default=0)),
                ('earnings', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='US_ValidPostBack',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('offerwall', models.CharField(max_length=300)),
                ('unique', models.CharField(max_length=300)),
                ('playerid', models.CharField(max_length=300)),
                ('client_wall', models.IntegerField()),
                ('reward', models.FloatField()),
                ('offer_name', models.CharField(max_length=300)),
                ('offer_id', models.CharField(max_length=300)),
            ],
        ),
    ]
