from django.urls import path

from .views import (
    CreateReactionDailyStatAPIView,
    CreateVoiceChatDailyStatAPIView,
    ReactionCountAPIView,
    VoiceChatRoomEntryExitAPIView,
)

urlpatterns = [
    path("voice-chat-entry-exit/", VoiceChatRoomEntryExitAPIView.as_view(), name="voice-chat-entry-exit"),
    path(
        "create-voice-chat-daily-stat/", CreateVoiceChatDailyStatAPIView.as_view(), name="create-voice-chat-daily-stat"
    ),
    path("reaction-count/", ReactionCountAPIView.as_view(), name="reaction-count"),
    path("create-reaction-daily-stat/", CreateReactionDailyStatAPIView.as_view(), name="create-reaction-daily-stat"),
]
