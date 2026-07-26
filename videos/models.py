from django.db import models


class Video(models.Model):
    """A video available on the platform, with its HLS conversion state."""

    class ProcessingStatus(models.TextChoices):
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
        return self.title
