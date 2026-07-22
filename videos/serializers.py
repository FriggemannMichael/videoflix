from rest_framework import serializers

from videos.models import Video


class VideoListSerializer(serializers.ModelSerializer):
    """Serialize the video metadata shown on the dashboard."""

    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = (
            'id',
            'created_at',
            'title',
            'description',
            'thumbnail_url',
            'category',
        )

    def get_thumbnail_url(self, video):
        if not video.thumbnail:
            return None
        request = self.context.get('request')
        url = video.thumbnail.url
        return request.build_absolute_uri(url) if request else url
