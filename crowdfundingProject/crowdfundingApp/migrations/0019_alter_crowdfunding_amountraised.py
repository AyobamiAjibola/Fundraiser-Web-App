# Generated by Django 5.1.2 on 2024-10-13 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("crowdfundingApp", "0018_alter_donation_user_alter_transaction_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="crowdfunding",
            name="amountRaised",
            field=models.DecimalField(
                blank=True, decimal_places=2, default=0, max_digits=10, null=True
            ),
        ),
    ]
