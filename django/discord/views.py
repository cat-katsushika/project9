from datetime import timedelta

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db.models import Sum
from django.utils import timezone

from .models import DailyVoiceChatStat, DiscordUser, VoiceChatSession
from .utils import send_message_to_discord


class VoiceChatRoomEntryExitAPIView(APIView):

    def post(self, request, *args, **kwargs):
        discord_user_id = request.data.get("discord_user_id")
        discord_username = request.data.get("discord_username")
        state = request.data.get("state")

        if discord_user_id is None or discord_username is None or state is None:
            return Response({"message": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)

        if state != "entry" and state != "exit":
            return Response({"message": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)

        discord_user, _ = DiscordUser.objects.get_or_create(discord_user_id=discord_user_id)
        discord_user.discord_username = discord_username
        discord_user.save()

        if state == "entry":

            # 未終了のセッション（入室のみのセッション）をすべて取得
            existing_sessions = VoiceChatSession.objects.filter(discord_user=discord_user, exit_time__isnull=True)

            if existing_sessions.exists():
                # 複数の入室のみのセッションがある場合、それらをすべて削除
                session_count = existing_sessions.count()
                existing_sessions.delete()
                # 古いセッションを削除したことをメッセージとして伝える
                message = f"{session_count}件の未終了セッションが削除され、新しい入室ログが記録されました。"
            else:
                # 既存のセッションがなければ、通常のメッセージ
                message = "新しい入室ログが記録されました。"

            # 新しい入室ログを作成
            VoiceChatSession.objects.create(discord_user=discord_user, entry_time=timezone.now())

            return Response({"message": message}, status=201)

        elif state == "exit":
            try:
                # まだ退出していないセッションを取得 (複数ある可能性があるためfilterを使用)
                sessions = VoiceChatSession.objects.filter(discord_user=discord_user, exit_time__isnull=True).order_by(
                    "entry_time"
                )

                if not sessions.exists():
                    return Response({"message": "入室情報が見つかりませんでした。退出処理は失敗しました。"}, status=400)

                # 最新のセッションを使用（最もエントリー時間が新しいものを使用）
                session = sessions.last()

                # 古いセッションを削除（最新のセッション以外のセッションを削除）
                sessions.exclude(id=session.id).delete()

                # 最新のセッションの退出時間を記録し、滞在時間を計算
                session.exit_time = timezone.now()
                session.duration = session.exit_time - session.entry_time
                session.save()

                second = int(session.duration.total_seconds())

                total_duration = VoiceChatSession.objects.filter(
                    discord_user=discord_user, exit_time__isnull=False
                ).aggregate(total_duration=Sum("duration"))["total_duration"]
                total_seconds = 0 if total_duration is None else int(total_duration.total_seconds())

                return Response(
                    {"message": "滞在時間が記録されました。", "duration": second, "total_seconds": total_seconds},
                    status=200,
                )

            except VoiceChatSession.DoesNotExist:
                # 入室記録がない場合のエラーメッセージ
                return Response({"message": "入室情報が見つかりませんでした。退出処理は失敗しました。"}, status=400)


class CreateVoiceChatDailyStatAPIView(APIView):

    def post(self, request, *args, **kwargs):
        today = timezone.localtime().date()
        yesterday = today - timedelta(days=1)
        previous_day = yesterday - timedelta(days=1)

        # 昨日のセッションを取得
        sessions = VoiceChatSession.objects.filter(exit_time__date=yesterday, exit_time__isnull=False)

        # ユーザーごとに滞在時間を集計
        user_stats = sessions.values("discord_user").annotate(total_duration=Sum("duration"))

        for stat in user_stats:
            discord_user_id = stat["discord_user"]
            discord_user = DiscordUser.objects.get(id=discord_user_id)
            yesterday_total_duration = stat["total_duration"]

            # 一昨日のデータを取得
            previous_stat = DailyVoiceChatStat.objects.filter(discord_user=discord_user, date=previous_day).first()

            # 一昨日のデータがある場合
            if previous_stat:
                total_duration = yesterday_total_duration + previous_stat.total_duration
            else:
                total_duration = yesterday_total_duration

            difference = yesterday_total_duration
            # データを保存

            DailyVoiceChatStat.objects.update_or_create(
                discord_user=discord_user,
                date=yesterday,
                defaults={"total_duration": total_duration, "difference_from_previous_day": difference},
            )

        response_data = {}

        # 上では昨日更新があった人のみデータを作成しているため，それ以外の人のStatを作成する
        for discord_user in DiscordUser.objects.all():
            previous_stat = DailyVoiceChatStat.objects.filter(discord_user=discord_user, date=previous_day).first()
            # おとといのデータがある場合
            if previous_stat:
                total_duration = previous_stat.total_duration
            else:
                total_duration = timedelta(0)
            difference = timedelta(0)

            yesterday_stat = DailyVoiceChatStat.objects.filter(discord_user=discord_user, date=yesterday).first()

            # 昨日の記録がまだない場合
            if not yesterday_stat:
                DailyVoiceChatStat.objects.create(
                    discord_user=discord_user,
                    date=yesterday,
                    total_duration=total_duration,
                    difference_from_previous_day=difference,
                )

            # ある場合
            else:
                total_duration = yesterday_stat.total_duration
                difference = yesterday_stat.difference_from_previous_day

            if not difference:
                difference = timedelta(0)

            response_data[discord_user.discord_username] = {
                "total_duration": int(total_duration.total_seconds()),
                "difference_from_previous_day": (difference.total_seconds()),
            }

        sorted_response_data = dict(
            sorted(response_data.items(), key=lambda item: item[1]["total_duration"], reverse=True)
        )

        text = ""
        text += f"VC総滞在時間ランキング（{yesterday.year:4d}年{yesterday.month:2d}月{yesterday.day:2d}日）\n"

        for index, (key, value) in enumerate(sorted_response_data.items()):
            duration_seconds = int(value["total_duration"])
            hours, remainder = divmod(duration_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            text += f"{index+1}. -> {hours:2d}時間 {minutes:2d}分 {seconds:2d}秒 -> "

            diff_from_previous_day_seconds = int(value["difference_from_previous_day"])
            if diff_from_previous_day_seconds > 0:
                diff_hours, diff_remainder = divmod(diff_from_previous_day_seconds, 3600)
                diff_minutes, diff_seconds = divmod(diff_remainder, 60)
                text += f"前日比: +{diff_hours:2d}時間 {diff_minutes:2d}分 {diff_seconds:2d}秒 -> "

            text += f"{key}\n"

        # 更新があるときだけ通知
        flag = False
        for key, value in sorted_response_data.items():
            if int(value["difference_from_previous_day"]) > 0:
                flag = True
                break

        if flag:
            send_message_to_discord(text=text, username="マーマルの犬")
        return Response(response_data, status=201)
