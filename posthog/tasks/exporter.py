import os
import uuid
import structlog
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from django.conf import settings


from posthog.celery import app
from posthog.models import Insight

logger = structlog.get_logger(__name__)

_driver = None


# TODO: This should be somehow run at build time to ensure the chrome binary is pre-downloaded
def get_driver():
    global _driver
    if not _driver:

        options = Options()
        options.headless = True

        _driver = webdriver.Chrome(
            service=Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()), options=options
        )

    return _driver


def _export_insight_task(insight_id: int) -> None:
    """
    Exporting an Insight means:
    1. Loading the Insight from the web app in a dedicated rendering mode
    2. Waiting for the page to have fully loaded before taking a screenshot to disk
    3. Loading that screenshot into memory and saving the data representation to the relevant Insight
    4. Cleanup: Remove the old file and close the browser session
    """
    image_id = uuid.uuid4()
    image_path = f"/tmp/{image_id}"
    insight = Insight.objects.get(id=insight_id)

    insight_page_token = "foobar"  # TODO: generate_one_off_token(insight)
    insight_url = f"{settings.SITE_URL}/exports/insights/?insight_id={insight.id}&team_id={insight.team.id}&token={insight_page_token}"

    # NOTE: Temp for testing
    insight_url = "http://localhost:8000/shared_dashboard/P_X_66syKP_M6Fk5UAqhnKSVNlvrTQ"

    logger.info(f"Exporting... {insight_url}")

    try:
        browser = get_driver()
        browser.set_window_size(1920, 1080)
        browser.get(insight_url)

        # TODO: Change this to something deterministic like a JS object check from the page that all insights have settled
        WebDriverWait(browser, 10).until(lambda x: x.find_element(By.CSS_SELECTOR, ".InsightCard"))
        browser.save_screenshot(image_path + ".png")

        os.remove(image_path)

    except Exception as err:
        logger.error("Export Error:", err)
        raise err


@app.task(ignore_result=True)
def export_insight_task(insight_id: int) -> None:
    _export_insight_task(insight_id=insight_id)
    logger.info("Done!")
