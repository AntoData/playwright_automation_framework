# conftest.py
import random
import pytest
import logging
from collections.abc import Generator
from pathlib import Path
from datetime import datetime
from playwright.async_api import ViewportSize
from playwright.sync_api import Page, Browser, BrowserContext
from utils import video_manager
from utils import config_adapter
from utils import settings_manager
from utils import logging_adapter
from utils import path_utils as path_utils
from utils import page_event_logging

@settings_manager.settings_manager(connector=config_adapter.ConfigFileAdapter,
                                   path=Path("config") / "config.ini",
                                   settings_list=["headless_mode",
                                                  "temp_video_path",
                                                  "final_video_path",
                                                  "network_and_console_logs",
                                                  "view_port_width",
                                                  "view_port_height",
                                                  "default_timeout"])
class TestSettings:
    """
    Manages the settings for the tests, such as headless mode and video
     paths.
    """
    settings: dict | None = None

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Pytest hook implementation to capture tests outcomes (pass/fail) and
     ºlog them.
    This function is called after each tests is executed, and it
    retrieves the tests result, attaches it to the tests item for later
    access, and logs the outcome using the logging adapter.
    :param item: The tests item object representing the tests being
     executed
    :type item: pytest.Item
    :param call: Object representing the tests call, containing
    information about the tests execution
    :type call: pytest.CallInfo
    :return:
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)
    log: logging.Logger = (
        logging_adapter.LoggingAdapter.get_logger())
    log.info(call)
    log.info(rep)

@pytest.fixture(scope="session")
def browser(browser_type) -> Generator[Browser, None, None]:
    """
    Defines a pytest fixture for the Playwright browser instance.
    This fixture is responsible for launching the browser with specific
     settings and closing it after the tests are done.
    :param browser_type: The type of browser to launch
    (e.g., Chromium, Firefox, WebKit)
    :type browser_type: Playwright's BrowserType
    :return: A generator that yields the browser instance for use in
    tests
    :rtype: Generator[Browser, None, None]
    """

    browser = browser_type.launch(
        headless=TestSettings.settings["headless_mode"].lower() == "true",
        slow_mo=0.5,
        args=["--disable-blink-features=AutomationControlled"],
    )
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def context(browser: Browser) \
        -> Generator[BrowserContext, None, None]:
    """
    Defines a pytest fixture for the Playwright browser context. This
    fixture is responsible for creating a new browser context for each
    tests function, with specific settings such as video recording,
    viewport size, and user agent. It also ensures that the temporary
    video directory exists before yielding the context for use in tests.
    :param browser: The Playwright browser instance provided by the
    'browser' fixture
    :type browser: Browser
    :return: Returns a generator that yields the browser context
    for use in tests
    :rtype: Generator[BrowserContext, None, None]
    """
    # Ensure the temporary video directory exists
    project_root = path_utils.get_project_root()
    temp_video_path = project_root / TestSettings.settings["temp_video_path"]
    temp_video_path.mkdir(parents=True, exist_ok=True)
    # Create a new browser context with the specified settings
    context = browser.new_context(
        record_video_dir=str(temp_video_path),  # always record
        viewport = ViewportSize(
            width=int(TestSettings.settings["view_port_width"]),
            height=int(TestSettings.settings["view_port_height"])
        ),
        accept_downloads=True,
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.6422.113 Safari/537.36"
        ),
    )
    yield context

def test_log_setup(request) -> None:
    """
    Initializes a log instance per test execution

    :param request: Request object provided by pytest, used to access
    tests metadata such as the tests name
    :type request: pytest's FixtureRequest
    :return:
    """
    timestamp: str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    project_root: Path = path_utils.get_project_root()
    log_file_path = project_root / "logs" / "{0}-{1}-{2}.log".format(
        request.node.name,
        timestamp,
        random.randint(0, 100000),
    )
    logging_adapter.LoggingAdapter.setup(
        log_file_path,
        also_console=TestSettings.settings[
                         "network_and_console_logs"].lower() == "true",
    )

def log_test_result(request) -> None:
    """
    Adds the result of the execution of a test to our logs

    :param request: Request object provided by pytest, used to access
    tests metadata such as the tests name
    :type request: pytest's FixtureRequest
    :return: None
    """
    log: logging.Logger = (
        logging_adapter.LoggingAdapter.get_logger())
    rep_call = getattr(request.node, "rep_call", None)

    if rep_call and rep_call.failed:
        log.error(f"⛔ TEST FAILED: {request.node.name}")
        if rep_call.longrepr:
            log.error(str(rep_call.longrepr))
    elif rep_call and rep_call.passed:
        log.info(f"🟩 TEST PASSED: {request.node.name}")
    else:
        log.warning(f"⚠️ NO OUTCOME: {request.node.name}")

    log.info("")


@pytest.fixture(scope="function")
def page(context: BrowserContext, request) -> Generator[Page, None, None]:
    """
    Defines a pytest fixture for the Playwright page. This fixture is
    responsible for creating a new page within the provided browser
    context for each tests function. After the tests function has
    completed, it finalizes the video recording by closing the page and
    context, and then moves the recorded video to a specified
    destination path with a name based on the tests name.
    :param context: The Playwright browser context provided by the
    'context' fixture
    :type context: BrowserContext
    :param request: Request object provided by pytest, used to access
    tests metadata such as the tests name
    :type request: pytest's FixtureRequest
    :return: A generator that yields the Playwright page for use in
    tests
    :rtype: Generator[Page, None, None]
    """
    # Create a new page within the provided browser context
    page = context.new_page()
    page.set_default_timeout(int(TestSettings.settings["default_timeout"]))
    # Logger setup
    test_log_setup(request)

    log: logging.Logger = logging_adapter.LoggingAdapter.get_logger()
    #
    page_event_logs = page_event_logging.attach_page_event_loggers(page)
    yield page

    # Test has finished execution, closing page
    page.close()

    # Logging the result of this test execution
    log_test_result(request)

    # Log console errors and network activity if the setting is enabled
    network_and_console_logs = (
        TestSettings.settings["network_and_console_logs"].lower() == "true"
    )

    # Adding network tab and console logs if requested
    if network_and_console_logs:
        page_event_logging.emit_page_event_logs(log, page_event_logs)

    # Move the recorded video to the destination path with a name
    # based on the tests name
    test_name: str = request.node.name
    video_manager.playwright_video_manager(page, test_name)
    # Close handlers safely
    for handler_ in list(log.handlers):
        handler_.close()
        log.removeHandler(handler_)
