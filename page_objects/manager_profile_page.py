import playwright.sync_api
from page_objects import page_object_template

class ManagerProfile(page_object_template.PageObjectTemplate):
    """
    Provides methods to interact with the profile page of
    a manager
    """

    def is_button_with_name_displayed(self, name: str) -> bool:
        """
        Returns True if the button with name specified is displayed
        :param name: Name of the button
        :type name: str
        :return: The button with name is displayed
        :rtype: bool
        """
        try:
            self.page.get_by_role("button", name=name).wait_for(
                state="visible", timeout=10000)
            return True
        except playwright.sync_api.TimeoutError:
            return False

    def click_button_with_name(self, name: str) -> None:
        """
        Clicks button with name specified
        :param name: Name of the button
        :type name: str
        :return: None
        """
        if self.is_button_with_name_displayed(name):
            self.page.get_by_role("button", name=name).click()
        else:
            raise playwright.sync_api.TimeoutError