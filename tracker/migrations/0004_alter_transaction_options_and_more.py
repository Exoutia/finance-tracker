# Generated by Django 4.2.16 on 2024-10-25 03:22

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("tracker", "0003_alter_transaction_created_at"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="transaction",
            options={"ordering": ["-date"]},
        ),
        migrations.RenameField(
            model_name="transaction",
            old_name="created_at",
            new_name="date",
        ),
    ]
