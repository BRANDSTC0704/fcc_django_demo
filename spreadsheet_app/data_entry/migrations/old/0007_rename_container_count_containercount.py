# Generated by Django 5.1.7 on 2025-03-11 14:05

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("data_entry", "0006_container_count_protocollist_delete_count_and_more"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Container_Count",
            new_name="ContainerCount",
        ),
    ]
