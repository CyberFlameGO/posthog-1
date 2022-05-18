from typing import Any

from django.http import HttpResponse
from rest_framework import mixins, serializers, viewsets
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from posthog.api.routing import StructuredViewSetMixin
from posthog.auth import PersonalAPIKeyAuthentication
from posthog.models.exported_asset import ExportedAsset
from posthog.permissions import ProjectMembershipNecessaryPermissions, TeamMemberAccessPermission


class ExportedAssetSerializer(serializers.ModelSerializer):
    """Standard ExportedAsset serializer that doesn't return key value."""

    class Meta:
        model = ExportedAsset
        fields = ["id", "dashboard_id", "insight_id", "export_type", "export_format", "created_at", "has_content"]


class ExportedAssetViewSet(mixins.RetrieveModelMixin, StructuredViewSetMixin, viewsets.GenericViewSet):
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
