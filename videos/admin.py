"""Admin configuration for the video catalogue.

Uploading a video through the admin is the only way videos enter the system,
so the form has to collect everything the dashboard needs and keep the fields
owned by the conversion pipeline out of the editor's hands.
"""

from django import forms
from django.contrib import admin

from videos.models import Video

UPLOAD_FIELDS = ('title', 'description', 'category', 'original_file')
PIPELINE_FIELDS = ('thumbnail', 'processing_status', 'processing_error')


class VideoAdminForm(forms.ModelForm):
    """Require every field the dashboard needs to display a video."""

    class Meta:
        """Bind the form to the video model with all editable fields."""

        model = Video
        fields = UPLOAD_FIELDS + PIPELINE_FIELDS

    def __init__(self, *args, **kwargs):
        """Mark the upload fields as required, whatever the model allows."""
        super().__init__(*args, **kwargs)
        for name in UPLOAD_FIELDS:
            self.fields[name].required = True


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Admin configuration for uploading and managing videos."""

    form = VideoAdminForm
    list_display = ('title', 'category', 'processing_status', 'created_at')
    list_filter = ('category', 'processing_status')
    # The conversion pipeline owns these fields, so they must not be editable.
    readonly_fields = ('processing_status', 'processing_error')
    fieldsets = (
        (
            'Upload',
            {
                'fields': UPLOAD_FIELDS,
                'description': 'All fields in this section are required.',
            },
        ),
        (
            'Processing',
            {
                'fields': PIPELINE_FIELDS,
                'description': (
                    'Filled in automatically after the upload: the thumbnail '
                    'and the HLS renditions are generated in the background, '
                    'and the status follows that job.'
                ),
            },
        ),
    )
