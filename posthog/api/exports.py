from typing import Any, Dict

from django.http import HttpResponse
from rest_framework import mixins, serializers, viewsets
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from posthog.api.routing import StructuredViewSetMixin
from posthog.auth import PersonalAPIKeyAuthentication
from posthog.event_usage import report_user_action
from posthog.models.exported_asset import ExportedAsset
from posthog.permissions import ProjectMembershipNecessaryPermissions, TeamMemberAccessPermission
from posthog.tasks import exporter


class ExportedAssetSerializer(serializers.ModelSerializer):
    """Standard ExportedAsset serializer that doesn't return content."""

    class Meta:
        model = ExportedAsset
        fields = ["id", "dashboard", "insight", "export_format", "created_at", "has_content"]
        read_only_fields = ["id", "created_at", "has_content"]

    def create(self, validated_data: Dict, *args: Any, **kwargs: Any) -> ExportedAsset:
        request = self.context["request"]
        validated_data["team_id"] = self.context["team_id"]

        if not validated_data.get("dashboard") and not validated_data.get("insight"):
            raise ValidationError("Either dashboard or insight is required for an export")

        instance: ExportedAsset = super().create(validated_data)

        exporter.export_task.delay(instance.id)

        report_user_action(
            request.user, "export created", instance.get_analytics_metadata(),
        )

        return instance


class ExportedAssetViewSet(
    mixins.RetrieveModelMixin, mixins.CreateModelMixin, StructuredViewSetMixin, viewsets.GenericViewSet
):
    queryset = ExportedAsset.objects.order_by("-created_at")
    serializer_class = ExportedAssetSerializer

    authentication_classes = [
        PersonalAPIKeyAuthentication,
        SessionAuthentication,
        BasicAuthentication,
    ]
    permission_classes = [IsAuthenticated, ProjectMembershipNecessaryPermissions, TeamMemberAccessPermission]

    @action(methods=["GET"], detail=True)
    def content(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instance = self.get_object()
        res = HttpResponse(instance.content, content_type=instance.export_format)
        res["Content-Disposition"] = f'attachment; filename="{instance.filename}"'

        return res
