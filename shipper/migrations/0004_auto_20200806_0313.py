# Generated by Django 3.0.7 on 2020-08-06 03:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shipper', '0003_auto_20200705_0703'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='name',
            field=models.TextField(help_text="Example: 'Nexus 5X', 'Nexus 6P'", max_length=100),
        ),
    ]
