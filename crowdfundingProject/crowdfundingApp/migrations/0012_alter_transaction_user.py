# Generated by Django 5.1.1 on 2024-10-12 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("crowdfundingApp", "0011_alter_transaction_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="transaction",
            name="user",
            field=models.TextField(max_length=255, null=True),
        ),
    ]