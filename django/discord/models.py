import uuid

from django.db import models


class DiscordUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    discord_user_id = models.CharField(max_length=255, unique=True)
    discord_username = models.CharField(max_length=255)

    def __str__(self):
        return self.discord_username


class VoiceChatSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    discord_user = models.ForeignKey(DiscordUser, on_delete=models.CASCADE)
    entry_time = models.DateTimeField()
    exit_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)

    def __str__(self):
        return f"Session for {self.discord_user.discord_username}"


class DailyVoiceChatStat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    discord_user = models.ForeignKey(DiscordUser, on_delete=models.CASCADE)
    date = models.DateField()
    total_duration = models.DurationField(default=0)
    difference_from_previous_day = models.DurationField(null=True, blank=True)

    class Meta:
        unique_together = ("discord_user", "date")

    def __str__(self):
        return f"{self.discord_user.discord_username} - {self.date}"
