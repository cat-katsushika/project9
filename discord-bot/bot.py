import os

import discord
import requests

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # メンバーの状態変更を受け取るために必要

client = discord.Client(intents=intents)

# グローバル変数としてチャンネルを定義
channel = None


@client.event
async def on_ready():
    global channel
    channel_id = int(os.getenv("DISCORD_CHANNEL_ID"))
    channel = client.get_channel(channel_id)
    print(f"Logged in as {client.user}")
    if channel is None:
        print("チャンネルが見つかりません。DISCORD_CHANNEL_IDを確認してください。")
    else:
        await channel.send("ボットがオンラインになりました。")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("check"):
        await message.channel.send("I'm alive!")
        await message.channel.send(f"チャンネル名: {message.channel}, チャンネルID: {message.channel.id}")


@client.event
async def on_voice_state_update(member, before, after):
    if channel is None:
        return

    # 状態の変化を検出
    if before.channel is None and after.channel is not None:
        # ユーザーがボイスチャンネルに参加した
        state = "entry"
    elif before.channel is not None and after.channel is None:
        # ユーザーがボイスチャンネルから退出した
        state = "exit"
        await channel.send(f"{member.name} が {before.channel.name} から退出しました。")
    elif before.channel != after.channel:
        # ユーザーがボイスチャンネルを移動した
        return
    else:
        # 状態に変化がない場合
        return

    # APIに送信するデータ
    data = {"discord_user_id": member.id, "discord_username": member.name, "state": state}

    # APIリクエストを送信
    try:
        res = requests.post("http://django:8000/api/discord/voice-chat-entry-exit/", data=data)
        if state == "exit" and res.status_code == 200:
            duration = res.json()["duration"]
            hours, remainder = divmod(duration, 3600)
            minutes, seconds = divmod(remainder, 60)

            await channel.send(f"{member.name}の滞在時間を記録しました -> 滞在時間: {hours}時間{minutes}分{seconds}秒")
    except requests.exceptions.RequestException as e:
        await channel.send(f"APIへの接続中にエラーが発生しました: {e}")


client.run(os.getenv("DISCORD_TOKEN"))
