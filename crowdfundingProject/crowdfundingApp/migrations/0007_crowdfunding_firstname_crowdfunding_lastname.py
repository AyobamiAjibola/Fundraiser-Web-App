# Generated by Django 5.1.1 on 2024-09-08 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("crowdfundingApp", "0006_remove_crowdfunding_user_crowdfunding_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="crowdfunding",
            name="firstName",
            field=models.TextField(default="", max_length=255),
        ),
        migrations.AddField(
            model_name="crowdfunding",
            name="lastName",
            field=models.TextField(default="", max_length=255),
        ),
    ]
