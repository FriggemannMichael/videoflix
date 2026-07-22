from django.urls import path

from videos.views import VideoListView

urlpatterns = [
    path('video/', VideoListView.as_view(), name='video_list'),
]
