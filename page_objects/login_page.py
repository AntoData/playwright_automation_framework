"""
This module contains the LoginPage class, which represents the login
page of a web application.
"""
import time
from page_objects import page_object_template
from playwright.sync_api import Page, expect

class LoginPage(page_object_template.PageObjectTemplate):
    """
    This class represents the login page of a web application.
    """

    # ids and paths for elements on the login page
    user_dropdown_id: str = "#userSelect"
    def __init__(self, page: Page, url: str):
        """
        Initializes the LoginPage instance and navigates to the
        specified URL.
        :param page: Playwright Page object representing the web page
        to be interacted with.
        :type page: Page
        :param url: URL of the login page to navigate to.
        :type url: str
        """
        super().__init__(page)
        self.log.info("Navigating to the login page at URL: '{0}'".format(
            url))
        self.page.goto(
            url,
            wait_until="networkidle",
        )

    def click_button_with_name(self, name: str) -> None:
        """
        Clicks the login button with the specified name.
        :param name: Name of the login button to click with.
        :type name: str
        :return: None
        """
        self.log.info("Clicking the login button with name: '{0}'".format(
            name))
        self.page.get_by_role("button", name=name).click()
        self.log.info("Button clicked successfully")

    def click_button_login_role(self, user_role: str) -> None:
        """
        Clicks the login button for a specific user role on the login
        page.
        :param user_role: The role of the user (e.g., "admin", "user")
        for which to click the login button.
        :type user_role: str
        :return: None
        """
        self.log.info("Trying to click the login button for user role: "
                 "'{0}'".format(user_role))
        button_name: str = ""
        if user_role.lower() == "manager":
            button_name = "Bank Manager"
        elif user_role.lower() == "customer":
            button_name = "Customer"
        button_name = button_name + " Login"
        self.click_button_with_name(button_name)

    def get_items_in_user_dropdown(self) -> list:
        """
        Retrieves the list of items available in the user dropdown menu
        on the login page.
        :return: A list of items in the user dropdown menu.
        :rtype: list
        """
        self.log.info("Retrieving items from the user dropdown menu")
        self.page.locator(self.user_dropdown_id).wait_for(state="visible",
                                                          timeout=15000)
        dropdown_items: list[str] = (self.page.locator(
            self.user_dropdown_id).locator("option").all_text_contents())
        self.log.info(f"Items retrieved from dropdown: {dropdown_items}")
        return dropdown_items

    def assert_user_in_dropdown(self, user_name: str) -> bool:
        """
        Asserts that a specific user name is present in the user dropdown
        menu on the login page.
        :param user_name: The name of the user to check for in the
        dropdown menu.
        :type user_name: str
        :return: True if the user name is found in the dropdown menu,
        False otherwise.
        :rtype: bool
        """
        self.log.info(f"Asserting that user '{user_name}' is present in "
                 "the dropdown menu")
        found: bool = False
        for i in range(0, 10):
            dropdown_items = self.get_items_in_user_dropdown()
            if user_name in dropdown_items:
                self.log.info(f"User '{user_name}' found in dropdown menu")
                found = True
                break
            else:
                self.log.warning(f"User '{user_name}' not found in dropdown "
                             f"menu yet, iteration = '{i}'")
                self.log.warning("Sleeping for 1 sec")
                time.sleep(2)
        return found

    def select_user_from_dropdown(self, user_name: str) -> None:
        """
        Selects a specific user from the user dropdown menu on the
        login page.
        :param user_name: The name of the user to select from the
        dropdown menu.
        :type user_name: str
        :return: None
        """
        self.log.info(f"Selecting user '{user_name}' from the dropdown "
                 "menu")
        self.page.locator(self.user_dropdown_id).select_option(
            label=user_name)
        self.log.info(f"User '{user_name}' selected successfully")