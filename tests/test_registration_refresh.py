import subprocess
import time
import urllib.error
import urllib.request
from uuid import uuid4

import pytest


@pytest.fixture(scope="session")
def local_server():
    port = 8765
    process = subprocess.Popen(
        [
            "uvicorn",
            "src.app:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        cwd="/workspaces/skills-getting-started-with-github-copilot",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    base_url = f"http://127.0.0.1:{port}"
    for _ in range(30):
        try:
            urllib.request.urlopen(f"{base_url}/activities")
            break
        except urllib.error.URLError:
            time.sleep(1)
    else:
        process.terminate()
        raise RuntimeError("Server did not start")

    yield base_url

    process.terminate()
    process.wait(timeout=5)


def test_registration_updates_card_without_refresh(local_server):
    playwright = pytest.importorskip("playwright")
    sync_playwright = playwright.sync_api.sync_playwright
    email = f"{uuid4().hex}@example.com"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto(f"{local_server}/")
            page.wait_for_selector("#activities-list")

            page.select_option("#activity", "Chess Club")
            page.fill("#email", email)
            page.click("button[type='submit']")

            page.wait_for_selector("#message.success")
            page.wait_for_function(
                "(email) => document.querySelector('#activities-list .activity-card')?.textContent?.includes(email)",
                arg=email,
            )

            card = page.locator("#activities-list .activity-card").filter(has_text="Chess Club").first
            assert email in card.inner_text()
        finally:
            browser.close()
