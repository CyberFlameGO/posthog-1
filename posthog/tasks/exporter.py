import structlog

from posthog.celery import app
from posthog.models import Insight

logger = structlog.get_logger(__name__)


def _export_insight_task(insight_id: int) -> None:
    insight = Insight.objects.get(id=insight_id)
    logger.info(f"Exporting... {insight.id}")

    # page = await browser.newPage()
    # await page.goto(
    #     "http://localhost:8000/shared_dashboard/P_X_66syKP_M6Fk5UAqhnKSVNlvrTQ", {"waitUntil": "networkidle0"}
    # )
    # await page.waitForSelector(".InsightCard")
    # await page.screenshot({"path": "example.png"})

    # dimensions = await page.evaluate(
    #     """() => {
    #     return {
    #         width: document.documentElement.clientWidth,
    #         height: document.documentElement.clientHeight,
    #         deviceScaleFactor: window.devicePixelRatio,
    #     }
    # }"""
    # )

    # logger.info(dimensions)
    # # >>> {'width': 800, 'height': 600, 'deviceScaleFactor': 1}
    # await browser.close()


@app.task(ignore_result=True)
def export_insight_task(insight_id: int) -> None:
    _export_insight_task(insight_id=insight_id)
    logger.info("Done!")
