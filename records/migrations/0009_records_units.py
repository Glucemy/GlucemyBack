# Generated by Django 4.0.4 on 2022-06-01 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0008_records_bolus_records_hc_rations'),
    ]

    operations = [
        migrations.AddField(
            model_name='records',
            name='units',
            field=models.FloatField(default=0),
        ),
    ]
