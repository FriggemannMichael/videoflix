from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from videos.cache import get_cached_video_list, set_cached_video_list
from videos.models import Video
from videos.serializers import VideoListSerializer


class VideoListView(ListAPIView):
    """List videos that have finished processing, most recent first."""

    serializer_class = VideoListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Video.objects.filter(
            processing_status=Video.ProcessingStatus.COMPLETED
        ).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        data = get_cached_video_list()
        if data is None:
            queryset = self.filter_queryset(self.get_queryset())
            data = list(self.get_serializer(queryset, many=True).data)
            set_cached_video_list(data)
        return Response(data)
