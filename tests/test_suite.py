import time
import pytest
from pathlib import Path
from datetime import datetime, timedelta
import playwright.sync_api
from utils import config_adapter
from utils import logging_adapter
from utils import settings_manager
from utils import test_data_adapter
from page_objects import login_page as lg, manager_profile_page
from page_objects import manager_profile_page as mpp
from page_objects import customer_profile_page as upp
from page_objects import transactions_page as tp
from page_objects import manager_add_customer_page as macp
from page_objects import manager_customers_page as mcp
from page_objects import navigation_elements as nav


@settings_manager.settings_manager(
    connector=config_adapter.ConfigFileAdapter,
                      path=Path("config") / "config.ini",
                      settings_list=["base_url"])
class TestSettings:
    """
    Settings class for the tests
    """
    settings: dict | None = None

@pytest.mark.parametrize("case", test_data_adapter.open_test_data_file(
    Path("test_data") / "login_test.json"))
def test_login(page, case):
    """
    Tests the login page for different users with different roles whose
    data is set up in the file test_data/login_test.json

    :param page: page object
    :param case: Corresponding test case
    :return: None
    """
    manager_button_names: list[str] = ["Add Customer", "Open Account",
                                       "Customers"]
    customer_button_names: list[str] = ["Transactions", "Deposit",
                                        "Withdrawl"]
    log = logging_adapter.LoggingAdapter.get_logger()
    log.info("Testing login to application")
    log.info("Test data = {0}".format(case))
    log.info("Opening url = {0}".format(TestSettings.settings["base_url"]))
    login_page = lg.LoginPage(page, TestSettings.settings["base_url"])
    manager_profile: mpp.ManagerProfile = manager_profile_page.ManagerProfile(
        page)
    customer_profile: upp.CustomerProfile = upp.CustomerProfile(page)
    # Logging in as a certain role
    login_page.click_button_login_role(case["user_role"])
    if case["user_role"] == "customer":
        # Logging in as customer
        log.info("Checking buttons displayed for managers are not displayed")
        for manager_button_name in manager_button_names:
            log.info("Checking button {0} not available for customer".format(
                manager_button_name))
            assert not manager_profile.is_button_with_name_displayed(
                manager_button_name)
            log.info("Assertion was correct")
        username: str = case["username"]
        log.info("Logging process for {0} with name {1}".format(
            case["user_role"], username))
        log.info("Asserting username = {0} exists in the dropdown".format(
            username))
        assert login_page.assert_user_in_dropdown(username)
        log.info("Username is part of the dropdown")
        # Selecting customer in corresponding test case
        login_page.select_user_from_dropdown(username)
        log.info("Asserting we have selected {0}".format(username))
        assert login_page.assert_user_in_dropdown(username)
        # Trying to log in
        log.info("Clicking the button Login")
        login_page.click_button_with_name("Login")
        log.info("Logged in")
        log.info("Asserting the information displayed about our customer is "
                 "correct")
        log.info("Asserting username displayed correctly: user_name = "
                 "{0}".format(username))
        assert customer_profile.get_username() == username
        log.info("Username was correctly displayed")
        log.info("Getting all accounts owned by customer")
        user_accounts: list[str] = customer_profile.get_user_accounts()
        log.info("User accounts = {0}".format(user_accounts))
        log.info("Getting all expected user accounts from test data json")
        expected_user_accounts: list[str] = [account["Account Number"]
                                             for account in case["accounts"]]
        log.info("Expected user accounts = {0}".format(expected_user_accounts))
        log.info("Asserting user accounts displayed match expected user"
                 " accounts")
        assert set(user_accounts) == set(expected_user_accounts)
        log.info("Assertion was correct")
        i: int = 0
        log.info("Checking information for each account is correct")
        for account in case["accounts"]:
            log.info("Checking account {0}".format(account["Account Number"]))
            if i != 0:
                log.info("We need to select the account in the dropdown")
                customer_profile.select_user_account(account["Account Number"])
                log.info("Account selected successfully in the dropdown")
            for key_ in account:
                log.info("Checking attribute {0}".format(key_))
                log.info("Expected {0}={1}".format(key_, account[key_]))
                actual_value: str = customer_profile.get_account_attribute(
                    key_)
                log.info("Actual {0}={1}".format(key_, actual_value))
                assert account[key_] == actual_value
                log.info("Assertion was correct")
            i += 1
        log.info("Checking buttons for customers are displayed")
        for button_name in customer_button_names:
            log.info("Checking button {0} is displayed".format(button_name))
            assert customer_profile.is_button_with_name_displayed(button_name)
            log.info("Assertion was correct")
    elif case["user_role"] == "manager":
        # Logging in as a bank manager
        log.info("Checking buttons for managers are displayed")
        for button_name in manager_button_names:
            log.info("Checking button {0} is displayed".format(button_name))
            assert manager_profile.is_button_with_name_displayed(button_name)
            log.info("Assertion was correct")
        log.info("Checking buttons for customers are not displayed")
        for button_name in customer_button_names:
            log.info("Checking button {0} is not displayed".format(
                button_name))
            assert not customer_profile.is_button_with_name_displayed(
                button_name)
            log.info("Assertion was correct")
    else:
        raise ValueError("User role set up in file is not recognized")

# These tests might be marked as expected to fail as there are several
# bugs regarding the transactions workflow
# @pytest.mark.xfail
@pytest.mark.parametrize("case", test_data_adapter.open_test_data_file(
    Path("test_data") / "transactions_data.json"))
def test_transactions(page, case):
    """
    Tests customers transactions, deposit, withdrawal and case when
    customer tries to withdraw more money than their balance in set
    account
    :param page: Playwright page fixture
    :param case: Test case to execute (all come from json file)
    :return:
    """
    log = logging_adapter.LoggingAdapter.get_logger()
    log.info("Testing login to application")
    log.info("Test data = {0}".format(case))
    log.info("Opening url = {0}".format(TestSettings.settings["base_url"]))
    login_page = lg.LoginPage(page, TestSettings.settings["base_url"])
    log.info("Logging in as a customer")
    login_page.click_button_login_role("customer")
    customer_profile: upp.CustomerProfile = upp.CustomerProfile(page)
    username: str = case["username"]
    log.info("Logging process for customer with name {0}".format(username))
    # Selecting customer in corresponding test case
    login_page.select_user_from_dropdown(username)
    # Trying to log in
    log.info("Clicking the button Login")
    login_page.click_button_with_name("Login")
    log.info("Logged in")
    customer_profile.select_user_account(case["Account Number"])
    log.info("Checking information for account before operation is correct")
    for key_ in ["Balance", "Currency"]:
        log.info("Checking attribute {0}".format(key_))
        log.info("Expected {0}={1}".format(key_, case[key_]))
        actual_value: str = customer_profile.get_account_attribute(
            key_)
        log.info("Actual {0}={1}".format(key_, actual_value))
        assert case[key_] == actual_value
        log.info("Assertion was correct")
    log.info("Clicking the button {0} to perform such operation".format(
        case["Operation"]))
    customer_profile.click_button_with_name(case["Operation"])
    log.info("Button was click, now trying to add the amount = {0} "
             "for the transaction".format(case["Amount"]))
    customer_profile.fill_amount_field(case["Amount"])
    operation_start_time: datetime = datetime.now().replace(microsecond=0)
    log.info("Operation started at: {0}".format(operation_start_time))
    # We remove 20 secs to make sure our operation will meet the range
    operation_start_time -= timedelta(seconds=20)
    log.info("This will be the lower range of dates to find this "
             "transaction = {0}".format(operation_start_time))
    operation_start_time_str: str = operation_start_time.strftime(
        "%Y-%m-%dT%H:%M:%S")
    operation: str = case["Operation"]
    # Todo: Known bug: Misspelled button as Withdrawl
    log.info("Trying to perform operation = {0} by click the button at "
             "the bottom".format(operation))
    customer_profile.click_submit_operation_button_with_name(operation)
    log.info("Button clicked")
    operation_end_time: datetime = datetime.now() + timedelta(seconds=1)
    operation_end_time_str: str = operation_end_time.strftime(
        "%Y-%m-%dT%H:%M:%S")
    log.info("Operation ended at: {0}".format(operation_end_time_str))
    expected_balance_after_operation: int = 0
    log.info("Working out expected balance after operation")
    if case["Operation"] == "Deposit":
        expected_balance_after_operation: str = str(int(case["Balance"]) +
                                                    int(case["Amount"]))
        log.info("After deposit, balance should be {0}".format(
            expected_balance_after_operation))
    elif case["Operation"] == "Withdraw":
        expected_balance_after_operation: str = str(int(case["Balance"]) -
                                                    int(case["Amount"]))
        log.info("After withdraw, balance should be {0}".format(
            expected_balance_after_operation))
    balance_after_operation: str = customer_profile.get_account_attribute(
        "Balance")
    if int(expected_balance_after_operation) > 0:
        if case["Operation"] == "Withdraw":
            customer_profile.assert_operation_result("Transaction successful")
            log.info("Withdraw successful")
        elif case["Operation"] == "Deposit":
            customer_profile.assert_operation_result(
                "{0}.*Successful".format(case["Operation"]))
            log.info("Deposit successful")
        else:
            raise ValueError("Operation set up in file is not recognized")
        log.info("Checking actual balance = {0} == "
                 "expected balance = {1}".format(
            balance_after_operation, balance_after_operation))
        assert (int(balance_after_operation) ==
                int(expected_balance_after_operation))
        log.info("Assertion was correct")

        log.info("Clicking the button Transactions")
        customer_profile.click_button_with_name("Transactions")
        transactions_page: tp.TransactionsPage = tp.TransactionsPage(page)

        # Transactions can take a while to be processed
        (row_found, transaction_type, transaction_amount,
         operation_datetime_str) =(
            transactions_page.get_transaction_at_row(
                operation_start_time_str, operation_end_time_str,0))
        assert row_found
        log.info("First row where the information of our most recent"
                 " transaction should be found")
        operation_data_time: datetime = datetime.strptime(
            operation_datetime_str, "%b %d, %Y %I:%M:%S %p")
        log.info("Checking Date Time is between the instant before we "
                 "clicked the button to perform the transaction and the"
                 " instant after")
        assert (operation_start_time <= operation_data_time <=
                operation_end_time)
        log.info("Assertion was correct")
        log.info("Checking that transaction amount is correct")
        assert transaction_amount == case["Amount"]
        log.info("Assertion was correct")
        log.info("Checking that transaction type is correct")
        if case["Operation"] == "Deposit":
            assert transaction_type == "Credit"
        elif case["Operation"] == "Withdraw":
            assert transaction_type == "Debit"
        else:
            raise ValueError("Unsupported operation = {0}".format(
                case["Operation"]))
        log.info("Transaction type is correct")

    else:
        log.info("In this case, our transaction cannot be successful")
        customer_profile.assert_operation_result(
            "Transaction Failed. You can not withdraw amount more than "
            "the balance.")
        log.info("Error message is correct")
        log.info("We check that our balance has not changed: balance = "
                 "{0}".format(case["Balance"]))
        assert (int(balance_after_operation) ==
                int(case["Balance"]))
        log.info("Balance has not changed, assertion was correct")

        # Now we need to check this failed transaction has not been
        # registered
        log.info("Click the button Transactions")
        customer_profile.click_button_with_name("Transactions")
        transactions_page: tp.TransactionsPage = tp.TransactionsPage(page)
        transactions_page.modify_start_time(operation_start_time_str)
        # As transactions might take a while to be registered we need
        # to check several times
        (row_found, transaction_type, transaction_amount,
         operation_datetime_str) = transactions_page.get_transaction_at_row(
            operation_start_time_str, operation_end_time_str, 0)
        assert not row_found
        log.info("Assertion was correct")

@pytest.mark.parametrize("case", test_data_adapter.open_test_data_file(
    Path("test_data") / "new_customers_data.json"))
def test_manager_create_customer(page, case):

    log = logging_adapter.LoggingAdapter.get_logger()
    log.info("Testing login to application")
    log.info("Test data = {0}".format(case))
    log.info("Opening url = {0}".format(TestSettings.settings["base_url"]))
    login_page = lg.LoginPage(page, TestSettings.settings["base_url"])
    manager_profile: mpp.ManagerProfile = manager_profile_page.ManagerProfile(
        page)
    customer_profile: upp.CustomerProfile = upp.CustomerProfile(page)
    # Logging in as a manager
    login_page.click_button_login_role("manager")
    manager_profile.click_button_with_name("Add Customer")
    form_add_customer: macp.AddCustomerPage = macp.AddCustomerPage(page)
    form_add_customer.fill_in_first_name(case["First Name"])
    form_add_customer.fill_in_last_name(case["Last Name"])
    form_add_customer.fill_in_post_code(str(case["Post Code"]))

    form_add_customer.click_form_button_with_name("Add Customer")
    customer_profile.click_button_with_name("Customers")
    customers_table: mcp.CustomersListSection = mcp.CustomersListSection(page)
    j: int = 0
    new_customer: dict | None = None
    while j < 3:
        try:
            log.info("Iteration j = {0}".format(j))
            new_customer: dict = customers_table.get_customer_data(case["First Name"], case["Last Name"])
        except (playwright.sync_api.TimeoutError, ValueError) as e:
            log.error(e)
            log.info("Customer creation was not processed yet")
            log.info("We will retry again")
            log.info("Let's wait 30 seconds")
            time.sleep(30)
            log.info("Reloading page")
            customers_table.page.reload()
            log.info("Page reloaded")
            log.info("Increasing retry counter")
            j+=1
        else:
            log.info("Customer found")
            log.info("Breaking the loop")
            break

    for key_ in new_customer:
        if key_ not in ["Account Number", "Delete Customer"]:
            assert new_customer[key_] == str(case[key_])
        elif key_ == "Account Number":
            assert new_customer[key_] == ""
        elif key_ == "Delete Customer":
            assert new_customer[key_] == "Delete"

    navigation_bar: nav.UpperNavigationElements = (
        nav.UpperNavigationElements(page))
    navigation_bar.click_button_with_name("Home")

    login_page.click_button_login_role("customer")
    login_page.select_user_from_dropdown(new_customer["First Name"] + " " + new_customer["Last Name"])
    login_page.click_button_with_name("Login")
    print("")
    customer_profile: upp.CustomerProfile = upp.CustomerProfile(page)
    assert (new_customer["First Name"] + " " + new_customer["Last Name"] ==
            customer_profile.get_username())
    customer_button_names: list[str] = ["Transactions", "Deposit",
                                        "Withdrawl"]
    for button_name in customer_button_names:
        log.info("Checking button {0} is displayed".format(button_name))
        assert not customer_profile.is_button_with_name_displayed(button_name)
        log.info("Assertion was correct")

