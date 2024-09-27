import requests

from django.conf import settings


def send_message_to_discord(text="メッセージの内容が指定されていません", username="BOT", avatar_url=""):
    # if settings.DEBUG:
    #     return
    # Discordのアイコン画像, べた書きでごめんなさい
    if avatar_url == "":
        avatar_url = "https://i.imgur.com/TzaLMxc.png"

    webhook_url = settings.DISCORD_WEBHOOK_URL

    data = {
        "content": text,
        "username": username,
        "avatar_url": avatar_url,
    }
    requests.post(webhook_url, data=data, timeout=10)
