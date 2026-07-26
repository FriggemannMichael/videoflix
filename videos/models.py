"""Database model for the video catalogue."""

from django.db import models


class Video(models.Model):
    """A video available on the platform, with its HLS conversion state.

    A video is created by uploading ``original_file`` in the Django admin.
    Saving it queues two background jobs: one extracts ``thumbnail`` from the
    first seconds of the file, the other transcodes the file into HLS
    renditions for every resolution in ``videos.hls.RESOLUTIONS``.

    ``processing_status`` follows that second job and is written by the job
    alone, never by hand. Only videos that reached ``COMPLETED`` are listed by
    the API and can be streamed; ``processing_error`` holds the message of the
    failure that moved a video to ``FAILED``.

    Attributes:
        title: Name shown on the dashboard and in the player.
        description: Longer text shown next to the title.
        category: Grouping the dashboard renders as a row, e.g. ``Drama``.
        original_file: The uploaded source file, the input of the pipeline.
        thumbnail: Preview image generated from the source file.
        created_at: Upload time; the dashboard sorts by it, newest first.
        updated_at: Time of the last change, including status changes.
        processing_status: Current state of the HLS conversion.
        processing_error: Error message of the last failed conversion.
    """

    class ProcessingStatus(models.TextChoices):
        """The states a video moves through while it is converted."""

        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100)
    original_file = models.FileField(upload_to='videos/original/')
    thumbnail = models.ImageField(upload_to='videos/thumbnails/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processing_status = models.CharField(
        max_length=20,
        choices=ProcessingStatus.choices,
        default=ProcessingStatus.PENDING,
        blank=True,
    )
    processing_error = models.TextField(blank=True, default='')

    def __str__(self):
        """Return the title, which is how the admin lists a video."""
        return self.title
