from playwright.sync_api import Locator, expect
from page_objects import page_object_template


class CustomersListSection(page_object_template.PageObjectTemplate):
    """
    Contains methods to interact with the page where all customers
    are listed that Bank Managers have access to
    """

    table_locator: str = "table"
    table_rows: dict = {
        "First Name": 0,
        "Last Name": 1,
        "Post Code": 2,
        "Account Number": 3,
        "Delete Customer": 4
    }

    def get_customer_row(self, first_name: str,
                         last_name: str | None = None) -> Locator:
        """
        Returns the row containing the customer details whose First
        and Last Names we have passed as parameters

        :param first_name: First Name of customer
        :type first_name: str
        :param last_name: Last Name of customer
        :type last_name: str | None
        :return: Row of customer details (Playwright Locator)
        :rtype: Locator
        """
        # First we get the table in the page as anchor
        table = self.page.locator(self.table_locator)
        # Then we get a list of all locators that represent rows in the
        # table
        rows = table.locator("tbody tr")

        # We filter rows by the ones whose first name matches the one
        # we are looking for
        rows = rows.filter(
            has=self.page.locator("td").nth(
                self.table_rows["First Name"]), has_text=first_name)

        # If Last Name was provided, we filter again by last name
        if last_name:
            rows = rows.filter(
                has=self.page.locator("td").nth(self.table_rows["Last Name"]),
                has_text=last_name)

        # If correct, the number of rows with this exact first and last
        # names should be 1
        expect(rows).to_have_count(1)
        count = rows.count()

        if count == 0:
            raise ValueError(
                f"Customer not found: {first_name} {last_name or ''}")

        if count > 1:
            raise ValueError(
                f"Multiple customers found: {first_name} {last_name or ''}")
        # We return the desired row
        return rows.first

    def get_column_from_row(self, row: Locator, column_name: str) -> str:
        """
        Returns the value of the specified column given the locator
        of a row in the table
        :param row: Locator of a row in the table
        :type row: Locator
        :param column_name: Name of the column
        :type column_name: str
        :return: Value of the specified column
        :rtype: str
        """
        return row.locator("td").nth(
            self.table_rows[column_name]).text_content()

    def get_customer_data(self, first_name: str, last_name: str | None
    = None) -> dict[str, str]:
        """
        Returns the customer details in the row in the table whose
        First Name and Last Names match
        :param first_name: Name of customer
        :type first_name: str
        :param last_name: Last Name of customer
        :type last_name: str | None
        :return: Dictionary of customer details
        :rtype: dict
        """
        # We get the row with that contains the information for our
        # customer
        row = self.get_customer_row(first_name, last_name)
        customer_data: dict[str, str] = {}
        # We add field by field this information to a dictionary
        for key_ in self.table_rows.keys():
            customer_data[key_] = self.get_column_from_row(row, key_)
        return customer_data
