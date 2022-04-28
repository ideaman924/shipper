# Generated by Django 3.2.12 on 2022-04-28 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shipper', '0035_remove_build_md5_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='build',
            name='md5sum',
            field=models.TextField(default='', max_length=32, verbose_name='MD5 hash'),
            preserve_default=False,
        ),
    ]
