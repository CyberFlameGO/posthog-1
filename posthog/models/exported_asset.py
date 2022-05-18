from django.db import models
from django.utils.text import slugify


class ExportedAsset(models.Model):
    class ExportType(models.TextChoices):
        DASHBOARD = "dashboard", "Dashboard"
        INSIGHT = "insight", "Insight"

    class ExportFormat(models.TextChoices):
        PNG = "image/png", "image/png"
        PDF = "application/pdf", "application/pdf"
        CSV = "text/csv", "text/csv"

    # Relations
    # TODO: Should we delete these on Cascade? What if the image is already sent somewhere...?
    team: models.ForeignKey = models.ForeignKey("Team", on_delete=models.CASCADE)
    dashboard = models.ForeignKey("posthog.Dashboard", on_delete=models.CASCADE, null=True)
    insight = models.ForeignKey("posthog.Insight", on_delete=models.CASCADE, null=True)

    # Content related fields
    export_type: models.CharField = models.CharField(max_length=16, choices=ExportType.choices)
    export_format: models.CharField = models.CharField(max_length=16, choices=ExportFormat.choices)
    content: models.JSONField = models.BinaryField(null=True)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True, blank=True)

    @property
    def has_content(self):
        return self.content is not None

    @property
    def filename(self):
        ext = self.export_format.split("/")[1]

        filename = "export"
        filename = f"{filename}-{slugify(self.dashboard.name)}" if self.dashboard else filename
        filename = f"{filename}-{slugify(self.insight.name)}" if self.insight else filename
        # TODO: Add timestamp?
        filename = f"{filename}.{ext}"

        return filename
