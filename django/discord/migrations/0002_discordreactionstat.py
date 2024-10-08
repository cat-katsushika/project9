# Generated by Django 4.2.16 on 2024-09-28 06:43

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("discord", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="DiscordReactionStat",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("date", models.DateField()),
                ("count", models.IntegerField(default=0)),
                (
                    "discord_user",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="discord.discorduser"),
                ),
            ],
            options={
                "unique_together": {("discord_user", "date")},
            },
        ),
    ]
