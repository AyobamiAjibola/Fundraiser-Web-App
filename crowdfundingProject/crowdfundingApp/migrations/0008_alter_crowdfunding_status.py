# Generated by Django 5.1.1 on 2024-09-19 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("crowdfundingApp", "0007_crowdfunding_firstname_crowdfunding_lastname"),
    ]

    operations = [
        migrations.AlterField(
            model_name="crowdfunding",
            name="status",
            field=models.TextField(default="inactive", max_length=255),
        ),
    ]
