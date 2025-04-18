# Generated by Django 5.1.7 on 2025-04-16 14:52

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="KuebelSession",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("comments", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="KuebelEintrag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("kuebel_art", models.CharField(max_length=100)),
                ("waschen_h", models.FloatField(default=0)),
                ("waschen_count", models.IntegerField(default=0)),
                ("instandh_h", models.FloatField(default=0)),
                ("instandh_count", models.IntegerField(default=0)),
                ("zerlegen_h", models.FloatField(default=0)),
                ("zerlegen_count", models.IntegerField(default=0)),
                (
                    "log",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="kuebel",
                        to="dateneingaben.kuebelsession",
                    ),
                ),
            ],
        ),
    ]
