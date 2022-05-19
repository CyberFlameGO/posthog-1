from unittest.mock import patch

from rest_framework import status

from posthog.models.dashboard import Dashboard
from posthog.models.exported_asset import ExportedAsset
from posthog.models.filters.filter import Filter
from posthog.models.insight import Insight
from posthog.test.base import APIBaseTest


@patch("posthog.api.exports.exporter")
class TestExports(APIBaseTest):
    exported_asset: ExportedAsset = None  # type: ignore
    dashboard: Dashboard = None  # type: ignore
    insight: Insight = None  # type: ignore

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        filter_dict = {
            "events": [{"id": "$pageview"}],
            "properties": [{"key": "$browser", "value": "Mac OS X"}],
        }
        cls.dashboard = Dashboard.objects.create(team=cls.team, name="example dashboard", created_by=cls.user)
        cls.insight = Insight.objects.create(
            filters=Filter(data=filter_dict).to_dict(), team=cls.team, created_by=cls.user
        )
        cls.exported_asset = ExportedAsset.objects.create(
            team=cls.team, dashboard_id=cls.dashboard.id, export_format="image/png"
        )

    def test_can_create_new_valid_export_dashboard(self, mock_exporter_task):
        response = self.client.post(
            f"/api/projects/{self.team.id}/exports", {"export_format": "image/png", "dashboard": self.dashboard.id}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(
            data,
            {
                "id": data["id"],
                "created_at": data["created_at"],
                "dashboard": self.dashboard.id,
                "export_format": "image/png",
                "has_content": False,
                "insight": None,
            },
        )

        mock_exporter_task.export_task.delay.assert_called_once_with(data["id"])

    def test_can_create_new_valid_export_insight(self, mock_exporter_task):
        response = self.client.post(
            f"/api/projects/{self.team.id}/exports", {"export_format": "application/pdf", "insight": self.insight.id}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(
            data,
            {
                "id": data["id"],
                "created_at": data["created_at"],
                "insight": self.insight.id,
                "export_format": "application/pdf",
                "has_content": False,
                "dashboard": None,
            },
        )

        mock_exporter_task.export_task.delay.assert_called_once_with(data["id"])

    def test_errors_if_missing_related_instance(self, mock_tasks):
        response = self.client.post(f"/api/projects/{self.team.id}/exports", {"export_format": "image/png"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {
                "attr": None,
                "code": "invalid_input",
                "detail": "Either dashboard or insight is required for an export",
                "type": "validation_error",
            },
        )

    def test_errors_if_bad_format(self, mock_tasks):
        response = self.client.post(f"/api/projects/{self.team.id}/exports", {"export_format": "not/allowed"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {
                "attr": "export_format",
                "code": "invalid_choice",
                "detail": '"not/allowed" is not a valid choice.',
                "type": "validation_error",
            },
        )
