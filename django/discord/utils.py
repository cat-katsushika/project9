from datetime import date

import requests
from table2ascii import table2ascii

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


def create_reaction_ranking_text(yesterday: date, sorted_response_data: dict) -> str:
    """Discordに通知するリアクション数ランキングの表を作成する関数"""

    text = ""
    text += f"# リアクション数ランキング   ({yesterday.year:4d}年{yesterday.month:2d}月{yesterday.day:2d}日)\n"

    header_list = ["Rank", "Username", "Reactions", "Change"]
    body_list = []

    for index, (key, value) in enumerate(sorted_response_data.items()):
        row_list = []

        total_counts = int(value["total_count"])
        yesterday_counts = int(value["yesterday_count"])

        row_list.append(index + 1)
        row_list.append(key)
        row_list.append(total_counts)
        row_list.append(yesterday_counts)
        body_list.append(row_list)

    output = table2ascii(
        header=header_list,
        body=body_list,
    )

    text += f"```\n{output}\n```"

    return text


def create_stay_time_ranking_text(yesterday: date, sorted_response_data: dict) -> str:
    """Discordに通知するVC総滞在時間ランキングの表を作成する関数"""

    text = ""
    text += f"# VC総滞在時間ランキング   ({yesterday.year:4d}年{yesterday.month:2d}月{yesterday.day:2d}日)\n"

    header_list = ["Rank", "Username", "Total Stay Time", "Change"]
    body_list = []

    for index, (key, value) in enumerate(sorted_response_data.items()):
        row_list = []

        duration_seconds = int(value["total_duration"])
        hours, remainder = divmod(duration_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        row_list.append(index + 1)
        row_list.append(key)
        row_list.append(f"{hours:2d}h {minutes:2d}m {seconds:2d}s")

        diff_from_previous_day_seconds = int(value["difference_from_previous_day"])
        if diff_from_previous_day_seconds > 0:
            diff_hours, diff_remainder = divmod(diff_from_previous_day_seconds, 3600)
            diff_minutes, diff_seconds = divmod(diff_remainder, 60)
            row_list.append(f"{diff_hours:2d}h {diff_minutes:2d}m {diff_seconds:2d}s")
        else:
            row_list.append("")

        body_list.append(row_list)

    output = table2ascii(
        header=header_list,
        body=body_list,
    )

    text += f"```\n{output}\n```"

    return text
