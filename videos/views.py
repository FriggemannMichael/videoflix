from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

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
