# Generated by Django 5.1.7 on 2025-04-18 13:42

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dateneingaben", "0002_kuebelart_alter_kuebeleintrag_kuebel_art"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="kuebelart",
            options={"ordering": ["id"]},
        ),
        migrations.AlterField(
            model_name="kuebelsession",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
