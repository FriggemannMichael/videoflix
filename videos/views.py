"""API views for listing videos and serving their HLS files.

All three views require authentication, so playback is only possible for
logged-in users. Videos that have not finished converting are treated as if
they did not exist, which keeps half-written renditions off the dashboard.
"""

from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from videos.cache import get_cached_video_list, set_cached_video_list
from videos.hls import RESOLUTIONS, SEGMENT_PATTERN, playlist_path, segment_path
from videos.models import Video
from videos.serializers import VideoListSerializer

PLAYLIST_CONTENT_TYPE = 'application/vnd.apple.mpegurl'
SEGMENT_CONTENT_TYPE = 'video/mp2t'


class VideoListView(ListAPIView):
    """List videos that have finished processing, most recent first."""

    serializer_class = VideoListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return the streamable videos, newest first."""
        return Video.objects.filter(
            processing_status=Video.ProcessingStatus.COMPLETED
        ).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        """Answer from the cache, filling it on a miss.

        The lookup happens after the permission check on purpose: caching the
        view itself would hand the payload to unauthenticated callers.
        """
        data = get_cached_video_list()
        if data is None:
            queryset = self.filter_queryset(self.get_queryset())
            data = list(self.get_serializer(queryset, many=True).data)
            set_cached_video_list(data)
        return Response(data)


class PlaylistView(APIView):
    """Serve the HLS playlist of a ready video for a given resolution."""

    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution):
        """Serve the playlist, or 404 for any video that is not ready."""
        get_object_or_404(
            Video, pk=movie_id, processing_status=Video.ProcessingStatus.COMPLETED
        )
        if resolution not in RESOLUTIONS:
            raise Http404
        path = playlist_path(movie_id, resolution)
        if not path.exists():
            raise Http404
        return FileResponse(path.open('rb'), content_type=PLAYLIST_CONTENT_TYPE)


class SegmentView(APIView):
    """Serve a single HLS segment of a ready video for a given resolution.

    Only names matching ``<digits>.ts`` are accepted, so a crafted segment
    name cannot walk out of the video's own directory.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution, segment):
        """Serve one segment, or 404 when it is not available."""
        get_object_or_404(
            Video, pk=movie_id, processing_status=Video.ProcessingStatus.COMPLETED
        )
        if resolution not in RESOLUTIONS:
            raise Http404
        if not SEGMENT_PATTERN.match(segment):
            raise Http404
        path = segment_path(movie_id, resolution, segment)
        if not path.exists():
            raise Http404
        return FileResponse(path.open('rb'), content_type=SEGMENT_CONTENT_TYPE)
