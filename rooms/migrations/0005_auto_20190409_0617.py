# Generated by Django 2.2 on 2019-04-09 06:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0004_auto_20190409_0614'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='password',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]
