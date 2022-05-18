import os
import uuid

import structlog
from django.conf import settings
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType

from posthog.celery import app
from posthog.exporter_utils import generate_exporter_token
from posthog.models.exported_asset import ExportedAsset

logger = structlog.get_logger(__name__)

_driver = None

TMP_DIR = "/tmp"  # NOTE: Externalise this to ENV var

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


def _export_task(exported_asset_id: int) -> None:
    """
    Exporting an Insight means:
    1. Loading the Insight from the web app in a dedicated rendering mode
    2. Waiting for the page to have fully loaded before taking a screenshot to disk
    3. Loading that screenshot into memory and saving the data representation to the relevant Insight
    4. Cleanup: Remove the old file and close the browser session
    """

    exported_asset = ExportedAsset.objects.get(pk=exported_asset_id)

    try:
        image_id = str(uuid.uuid4())
        image_path = os.path.join(TMP_DIR, f"{image_id}.png")

        url_to_render = None
        screenshot_width = 800

        if not os.path.exists(TMP_DIR):
            os.makedirs(TMP_DIR)

        if exported_asset.export_type == "insight":
            # TODO: this
            url_to_render = "http://localhost:8000/shared_dashboard/P_X_66syKP_M6Fk5UAqhnKSVNlvrTQ"
            wait_for_css_selector = ".InsightCard"
            screenshot_width = 800

        elif exported_asset.export_type == "dashboard":
            token = generate_exporter_token("dashboard", exported_asset.dashboard.id)
            url_to_render = f"{settings.SITE_URL}/shared_dashboard/{token}"
            wait_for_css_selector = ".InsightCard"
            screenshot_width = 1920
        else:
            raise Exception(f"Export of type {exported_asset.export_type} not supported")

        logger.info(f"Exporting... {exported_asset.export_type} {exported_asset.id}")

        screenshot_width = 800

        browser = get_driver()
        browser.set_window_size(screenshot_width, screenshot_width)
        browser.get(url_to_render)
        # TODO: Change this to something deterministic like a JS object check from the page that all insights have settled
        WebDriverWait(browser, 10).until(lambda x: x.find_element(By.CSS_SELECTOR, wait_for_css_selector))

        height = browser.execute_script("return document.body.scrollHeight")
        browser.set_window_size(screenshot_width, height)
        browser.save_screenshot(image_path)

        with open(image_path, "rb") as image_file:
            image_data = image_file.read()

        exported_asset.content = image_data
        exported_asset.save()

        os.remove(image_path)

    except Exception as err:
        # Ensure we clean up the tmp file in case anything went wrong
        if os.path.exists(image_path):
            os.remove(image_path)

        logger.error(f"Export Error: {err}")
        raise err


@app.task(ignore_result=True)
def export_task(exported_asset_id: int) -> None:
    _export_task(exported_asset_id)
