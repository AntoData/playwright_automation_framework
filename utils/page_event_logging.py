import logging
from dataclasses import dataclass
from playwright.sync_api import ConsoleMessage, Page, Request, Response


@dataclass
class PageEventLogs:
    """
    Manages logging of page events
    """
    console_errors: list[str]
    network_entries: list[str]

def attach_page_event_loggers(page: Page) -> PageEventLogs:
    """
    Attaches page event logging adapter to the logging module
    :param page: Playwiki page object
    :return: PageEventLogs
    :rtype: PageEventLogs
    """
    logs = PageEventLogs(console_errors=[], network_entries=[])

    def console_error_handler(msg: ConsoleMessage) -> None:
        """
        Handler for console errors
        :param msg: ConsoleMessage object
        :type msg: ConsoleMessage
        :return: None
        """
        if msg.type == "error":
            logs.console_errors.append(msg.text)

    def network_tab_request_handler(req: Request) -> None:
        """
        Handler for network tab request
        :param req: Request object
        :type req: Request
        :return: None
        """
        logs.network_entries.append(f"{req.method}: {req.url}")

    def network_tab_response_handler(res: Response) -> None:
        """
        Handler for network tab response
        :param res: Response object
        :type res: Response
        :return: None
        """
        logs.network_entries.append(f"{res.status}: {res.url}")

    # Attaching handlers to page events
    page.on("console", console_error_handler)
    page.on("request", network_tab_request_handler)
    page.on("response", network_tab_response_handler)
    # Returning resulting logs
    return logs


def emit_page_event_logs(log: logging.Logger, logs: PageEventLogs) \
        -> None:
    log.info("-------------Browser logs-------------")
    log.info(" -----BROWSER CONSOLE ERRORS----- ")
    for err in logs.console_errors:
        log.error(err)

    log.info(" -----NETWORK TAB----- ")
    for entry in logs.network_entries:
        log.info(entry)
