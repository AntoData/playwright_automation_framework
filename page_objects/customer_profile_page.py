import re
import playwright.sync_api
from playwright.sync_api import expect
from page_objects import page_object_template

class CustomerProfile(page_object_template.PageObjectTemplate):
    """
    This class provides methods to interact with the profile page of
    a user
    """

    username_label_selector: str = "span.fontBig"
    accounts_dropdown_id: str = "#accountSelect"
    account_attribute_xpath: str = \
        "//text()[contains(., '{0}')]/following::strong"

    def get_username(self) -> str:
        """
        Returns the username
        :return: The name of the user that has logged in
        :rtype: str
        """
        return (
            self.page.locator(
                self.username_label_selector).text_content().strip())

    def get_user_accounts(self) -> list[str]:
        """
        Returns the list of accounts that the user owns
        :return: The list of accounts that the user has logged in
        :rtype: list[str]
        """
        return self.page.locator(
            self.accounts_dropdown_id).locator("option").all_text_contents()

    def select_user_account(self, account: str) -> None:
        """
        Selects the account sent as input in the dropdown for
        user accounts
        :param account: Id of the account
        :type account: str
        :return: None
        """
        self.page.locator(self.accounts_dropdown_id).select_option(
            label=account)

    def get_account_attribute(self, attribute: str) -> str:
        """
        Returns the attribute requested of the account selected
        previously
        :param attribute: Of the account selected
        :type attribute: str
        :return: Value of the attribute requested
        """

        return self.page.locator(
            self.account_attribute_xpath.format(
                attribute)).first.text_content().strip()

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

    def fill_amount_field(self, amount: str) -> None:
        """
        Fills the amount field
        :param amount: Amount to be filled
        :type amount: str
        :return: None
        """
        self.page.locator("form").get_by_role("spinbutton").fill(amount)

    def click_submit_operation_button_with_name(self, name: str) -> None:
        """
        Clicks submit operation button with name specified
        :param name: Name of the button
        :type name: str
        :return: None
        """
        self.page.locator("form").get_by_role("button", name=name).click()

    def assert_operation_result(self, result: str) -> None:
        """
        Asserts operation result displays the message in result
        :param result: Expected result of the operation
        :type result: str
        :return: None
        """
        expect(self.page.locator("span.error")).to_have_text(
            re.compile(result),
            timeout=10_000
        )