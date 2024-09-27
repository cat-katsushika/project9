from django.contrib import admin

from .models import DailyVoiceChatStat, DiscordUser, VoiceChatSession


@admin.register(DiscordUser)
class DiscordUserAdmin(admin.ModelAdmin):
    list_display = ("discord_user_id", "discord_username")
    search_fields = ("discord_user_id", "discord_username")


@admin.register(VoiceChatSession)
class VoiceChatSessionAdmin(admin.ModelAdmin):
    list_display = ("discord_user", "entry_time", "exit_time", "duration")
    search_fields = ("discord_user__discord_user_id", "discord_user__discord_username")
    list_filter = ("entry_time", "exit_time")


@admin.register(DailyVoiceChatStat)
class DailyVoiceChatStat(admin.ModelAdmin):
    list_display = ("discord_user", "date")
