from django.urls import path

from .views import CreateVoiceChatDailyStatAPIView, VoiceChatRoomEntryExitAPIView

urlpatterns = [
    path("voice-chat-entry-exit/", VoiceChatRoomEntryExitAPIView.as_view(), name="voice-chat-entry-exit"),
    path(
        "create-voice-chat-daily-stat/", CreateVoiceChatDailyStatAPIView.as_view(), name="create-voice-chat-daily-stat"
    ),
]
