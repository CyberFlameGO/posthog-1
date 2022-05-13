from django.db import models


class ExportedAsset(models.Model):
    class ExportType(models.TextChoices):
        DASHBOARD = "dashboard", "Dashboard"
        INSIGHT = "insight", "Insight"

    class ExportFormat(models.TextChoices):
        PNG = "png", "PNG"
        PDF = "pdf", "PDF"
        CSV = "csv", "CSV"

    # Relations
    # TODO: Should we delete these on Cascade? What if the image is already sent somewhere...?
    dashboard = models.ForeignKey("posthog.Dashboard", on_delete=models.CASCADE, null=True)
    insight = models.ForeignKey("posthog.Insight", on_delete=models.CASCADE, null=True)

    # Content related fields
    export_type: models.CharField = models.CharField(max_length=16, choices=ExportType.choices)
    export_format: models.CharField = models.CharField(max_length=16, choices=ExportFormat.choices)
    content: models.JSONField = models.BinaryField(null=True)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True, blank=True)
