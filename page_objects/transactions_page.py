import playwright.sync_api

from page_objects import page_object_template

class TransactionsPage(page_object_template.PageObjectTemplate):
    """
    Contains methods to interact with the transactions page
    """
    start_time_date_input_id: str = "#start"
    end_time_date_input_id: str = "#end"
    table_row_id: str = "#anchor{0}"
    elements_vs_position_table: dict = {
        "Date-Time": 0,
        "Amount": 1,
        "Transaction Type": 2,
    }

    def modify_start_time(self, start_time: str):
        """
        Modifies the start time of the filter in the transactions table
        :param start_time: Start time of the date filter in the
        transactions table:
        :type start_time: str
        :return: None
        """
        self.page.locator(self.start_time_date_input_id).fill(start_time)

    def modify_end_time(self, end_time: str):
        """
        Modifies the end time of the filter in the transactions table
        :param end_time: End time of the date filter in the table
        :type end_time: str
        :return: None
        """
        self.page.locator(self.end_time_date_input_id).fill(end_time)

    def get_row_nth_i(self, i: int) -> playwright.sync_api.Locator:
        """
        Gets the row in the table in position i
        :param i: Position of the row in the table
        :type i: int
        :return: Locator of the row in the table
        :rtype: Locator
        """
        return self.page.locator(self.table_row_id.format(i))

    def get_data_from_row_id(self, i: int, column_name: str) -> str:
        """
        Gets the data whose column has column name from the row i
        :param i: Number of row in the table (starts with 0)
        :type i: int
        :param column_name: Name of the column in the row i
        :type column_name: str
        :return: Content of the cell in such position
        :rtype: str
        """
        return self.get_row_nth_i(i).locator("td").nth(
            self.elements_vs_position_table[column_name]).text_content()