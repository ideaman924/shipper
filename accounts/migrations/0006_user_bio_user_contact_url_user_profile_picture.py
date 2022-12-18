# Generated by Django 4.1.4 on 2022-12-18 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0005_user_full_access_to_devices"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="bio",
            field=models.TextField(
                blank=True, help_text="Short bio about yourself!", max_length=500
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="contact_url",
            field=models.URLField(
                blank=True,
                help_text="Where users should contact you.<br>Example: https://t.me/@example, mailto:john.appleseed@example.com ",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="profile_picture",
            field=models.URLField(blank=True, help_text="URL to profile picture."),
        ),
    ]
