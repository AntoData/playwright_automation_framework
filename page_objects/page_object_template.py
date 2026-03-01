"""
This module defines the PageDefinition abstract base class, which serves
as a blueprint for defining page_objects objects in a web automation
framework.
"""
import abc
import logging

import playwright.sync_api

from utils import logging_adapter
from playwright.sync_api import Page, expect


class PageObjectTemplate(abc.ABC):
    """
    Abstract base class that defines the interface for page objects in
     a web automation framework. Subclasses must implement the necessary
    methods to interact with specific web pages
    """
    def __init__(self, page: Page):
        """
        Initializes the PageObjectTemplate instance with a Playwright
        Page object.
        :param page: Playwright Page object representing the
        web page_objects to be interacted with.
        :type page: Page
        """
        self.page: Page = page
        self.log: logging.Logger = logging_adapter.LoggingAdapter.get_logger()

    def find_locator_or_reload(self, locator: playwright.sync_api.Locator,
                               n_times: int, timeout: int):
        for _ in range(0, n_times):
            try:
                expect(locator).to_be_visible(
                    timeout=timeout)
            except (playwright.sync_api.TimeoutError, AssertionError):
                self.page.reload(wait_until="domcontentloaded")
            else:
                break