"""Serializers for the video API."""

from rest_framework import serializers

from videos.models import Video


class VideoListSerializer(serializers.ModelSerializer):
    """Serialize the video metadata shown on the dashboard."""

    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        """Expose only the fields the dashboard renders."""

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
        """Return an absolute thumbnail URL, or None while none exists yet.

        The URL has to be absolute because the frontend is served from a
        different host than the API.
        """
        if not video.thumbnail:
            return None
        request = self.context.get('request')
        url = video.thumbnail.url
        return request.build_absolute_uri(url) if request else url
