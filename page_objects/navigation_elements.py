"""
This module defines the UpperNavigationElements class, which provides
methods to interact with the upper navigation bar of a web application.
"""
from page_objects import page_object_template

class UpperNavigationElements(page_object_template.PageObjectTemplate):
    """
    This class provides methods to interact with the upper navigation
    bar
    """
    def click_button_with_name(self, name: str) -> None:
        """
        Clicks a button in the upper navigation bar based on its name.
        :param name: Name of the button to be clicked.
        :type name: str
        :return: None
        """
        self.log.info("Trying to click button with name: '{0}' in the "
                 "upper navigation bar".format(name))
        self.page.get_by_role("button", name=name).click()
        self.log.info("Button clicked successfully")