# Generated by Django 5.1.7 on 2025-03-17 08:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("data_entry", "0010_alter_employee_break_time"),
    ]

    operations = [
        migrations.AlterField(
            model_name="employee",
            name="break_time",
            field=models.FloatField(default=0.5, null=True),
        ),
    ]
