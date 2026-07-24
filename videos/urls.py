from django.urls import path

from videos.views import PlaylistView, VideoListView

urlpatterns = [
    path('video/', VideoListView.as_view(), name='video_list'),
    path(
        'video/<int:movie_id>/<str:resolution>/index.m3u8',
        PlaylistView.as_view(),
        name='video_playlist',
    ),
]
