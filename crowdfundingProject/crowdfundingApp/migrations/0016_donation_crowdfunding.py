# Generated by Django 5.1.2 on 2024-10-13 10:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("crowdfundingApp", "0015_remove_crowdfunding_donations"),
    ]

    operations = [
        migrations.AddField(
            model_name="donation",
            name="crowdfunding",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="donations",
                to="crowdfundingApp.crowdfunding",
            ),
        ),
    ]
