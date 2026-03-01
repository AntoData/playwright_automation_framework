from datetime import datetime

import playwright.sync_api

from page_objects import page_object_template

class TransactionsPage(page_object_template.PageObjectTemplate):
    """
    Contains methods to interact with the transactions page
    """
    transaction_table_datetime_format: str = "%b %d, %Y %I:%M:%S %p"
    filter_input_datetime_format: str = "%Y-%m-%dT%H:%M:%S"
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
        self.find_locator_or_reload(self.get_row_nth_i(i).locator("td").nth(
            self.elements_vs_position_table[column_name]), 60, 10)
        return self.get_row_nth_i(i).locator("td").nth(
            self.elements_vs_position_table[column_name]).text_content()

    def get_transaction_at_row(self, start, end, i):
        operation_datetime_str: str | None = None
        transaction_amount: str | None = None
        transaction_type: str | None = None
        row_found: bool = False
        for _ in range(0, 20):
            try:
                self.log.info(("Modifying the start time in the filter to = "
                             "{0}".format(end)))
                # Todo: KNOWN BUG -> (URL to bug)
                #  If we modify the endtime to a period after the last
                #  transaction was performed, whole table goes blank

                # self.modify_end_time(operation_end_time_str)
                self.log.info("Trying to get information from the first row in the"
                         " table")
                self.modify_start_time(start)
                self.log.info("Trying to get Date Time")
                operation_datetime_str: str = (
                    self.get_data_from_row_id(
                        i, "Date-Time"))
                operation_data_time: datetime = datetime.strptime(
                    operation_datetime_str,
                    self.transaction_table_datetime_format,
                )
                operation_start_time: datetime = datetime.strptime(
                    start,
                    self.filter_input_datetime_format,
                )
                assert operation_start_time <= operation_data_time
                self.log.info("Date Time = {0}".format(operation_datetime_str))
                self.log.info("Trying to get column Amount")
                transaction_amount: str = (
                    self.get_data_from_row_id(
                        i, "Amount"))
                self.log.info("Amount = {0}".format(transaction_amount))
                self.log.info("Trying to get column TransactionType")
                transaction_type: str = self.get_data_from_row_id(
                    i, "Transaction Type")
                self.log.info("Transaction Type = {0}".format(transaction_type))
            except (playwright.sync_api.TimeoutError, AssertionError,
                    ValueError) as e:
                self.log.error(e)
                self.log.info("Transaction not registered yet")
            else:
                self.log.info("Transaction found")
                row_found = True
                break

        return row_found, transaction_type, transaction_amount, operation_datetime_str
