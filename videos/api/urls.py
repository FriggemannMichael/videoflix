"""URL routes for the video list and for HLS delivery.

The playlist and segment paths carry no trailing slash because the players
request the segments relative to the playlist, exactly as written in it.
"""

from django.urls import path

from videos.api.views import PlaylistView, SegmentView, VideoListView

urlpatterns = [
    path('video/', VideoListView.as_view(), name='video_list'),
    path(
        'video/<int:movie_id>/<str:resolution>/index.m3u8',
        PlaylistView.as_view(),
        name='video_playlist',
    ),
    path(
        'video/<int:movie_id>/<str:resolution>/<str:segment>',
        SegmentView.as_view(),
        name='video_segment',
    ),
]
