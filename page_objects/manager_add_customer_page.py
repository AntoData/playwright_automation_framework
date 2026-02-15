from playwright.sync_api import Locator
from page_objects import page_object_template


class AddCustomerPage(page_object_template.PageObjectTemplate):
    """
    Contains methods to interact with the form to add customers
    """
    form_ng_model_field_locator: str = "input[ng-model='{0}']"
    form_fields: dict = {
        "first_name": "fName",
        "last_name": "lName",
        "post_code": "postCd"
    }

    def find_form(self) -> Locator:
        """
        Finds the form to fill with new customer data
        :return: Locator of such form
        :rtype: Locator
        """
        return self.page.locator("form").filter(
            has=self.page.locator("[ng-model='fName']"))

    def fill_in_form_field(self, field: str, value: str) -> None:
        """
        Fills in the field given in the form with the value given
        :param field: Field name
        :type field: str
        :param value: Value of the field
        :type value: str
        :return: None
        """
        form = self.find_form()
        locator_ = self.form_ng_model_field_locator.format(field)
        form.locator(locator_).fill(value)

    def fill_in_first_name(self, first_name: str) -> None:
        """
        Fills in the first_name given in the form with the value given

        :param first_name: First name
        :type first_name: str
        :return: None
        """
        self.fill_in_form_field(self.form_fields["first_name"],
                                first_name)

    def fill_in_last_name(self, last_name: str) -> None:
        """
        Fills in the last_name given in the form with the value given
        :param last_name: Last name
        :type last_name: str
        :return: None
        """
        self.fill_in_form_field(self.form_fields["last_name"], last_name)

    def fill_in_post_code(self, post_code: str) -> None:
        """
        Fills in the post_code given in the form with the value given
        :param post_code: Post code
        :return: None
        """
        self.fill_in_form_field(self.form_fields["post_code"], post_code)

    def click_form_button_with_name(self, name: str) -> None:
        """
        Clicks button in the form with a given name
        :param name: Name of the button
        :type name: str
        :return: None
        """
        form = self.find_form()
        form.get_by_role("button", name=name).click()