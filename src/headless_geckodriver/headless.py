import os
import logging
from typing import List, Optional, Union
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

from . import geckodriver


logger = logging.getLogger(__name__)

# Set the log directory
root_dir = os.path.dirname(os.path.abspath(__file__))
logs_dir = os.path.join(root_dir, "var", "logs")
if os.path.exists(logs_dir) is False:
    os.makedirs(logs_dir, exist_ok=True)

gecko_logs = os.path.join(logs_dir, "geckodriver.log")

# Get the geckodriver and firefox paths
geckodriver_path = geckodriver.get_binary_path()
firefox_path = geckodriver.get_firefox_path()
default_webdriver_options = [
    "--headless",
    "--disable-gpu",
    "--disable-extensions",
]

# Check if the paths are valid
if geckodriver_path is None and firefox_path is None:
    raise Exception("Geckodriver and Firefox not found")

elif geckodriver_path is None:
    raise Exception("Geckodriver not found")

elif firefox_path is None:
    raise Exception("Firefox not found")


def setup_webdriver(
    webdriver_options: Optional[List[str]] = None,
) -> webdriver.Firefox:
    """Generate a webdriver instance.

    Args:
        webdriver_options (List[str], optional): List of options to pass to the
            webdriver. Defaults to None.
    Returns:
        webdriver.Firefox: A webdriver instance.
    """
    # Set the webdriver options
    if webdriver_options is None:
        webdriver_options = default_webdriver_options

    # Generate the webdriver
    service = Service(
        executable_path=geckodriver_path,
        log_path=gecko_logs,
    )
    options = webdriver.FirefoxOptions()
    for option in webdriver_options:
        options.add_argument(option)

    options.binary_location = firefox_path
    driver = webdriver.Firefox(
        options=options,
        service=service,
    )
    return driver


def get_page(target_url: str):
    # Generate the webdriver
    driver = setup_webdriver()

    # Load the target URL
    driver.get(target_url)

    # Return the driver
    return driver


def handle_element_untils(
    driver: webdriver.Firefox, *untils: tuple, timeout: int = 20
):
    element = None
    try:
        if len(untils) > 0:
            element = WebDriverWait(driver, timeout).until(
                *untils,
            )
        else:
            element = WebDriverWait(driver, timeout)

        # Alternative: Wait for an element to be present on the page
        # element = WebDriverWait(driver, 20).until(
        #     EC.presence_of_element_located((By.ID, "element_id"))
        # )
        #
        # Alternative: Wait for an element to be clickable
        # element = WebDriverWait(driver, 20).until(
        #     EC.element_to_be_clickable((By.CLASS_NAME, "element_id"))
        # )
        #
        # Alternative: Wait for an element to be visible
        # element = WebDriverWait(driver, 20).until(
        #     EC.visibility_of_element_located((By.ID, "element_id"))
        # )
    except Exception as err:
        logger.error("Failed to load page: " + str(err))

    return element


def get_page_source(target_url: str, timeout: int = 20) -> Optional[str]:
    """Get the page source of a target URL.

    Args:
        target_url (str): The target URL.
    Returns:
        Optional[str]: The page source.
    """

    driver = get_page(target_url)
    element = handle_element_untils(driver, timeout=timeout)

    source = None
    # Get the page source
    if element is not None:
        source = driver.page_source

    driver.quit()
    return source


def get_http_requests(target_url: str) -> Union[List[dict], None]:
    """Get the HTTP requests made by the browser during a test.

    Args:
        target_url (str): The target URL.
    Returns:
        Union[List[dict], None]: The HTTP requests or None if the page failed
            to load.
    """
    # Generate the webdriver
    driver = get_page(target_url)
    element = handle_element_untils(driver, timeout=20)

    page_requests = None
    # Get the page requests
    if element is not None:
        page_requests = driver.requests

    driver.quit()
    return page_requests


# TODO: Implement get_full_page_screenshot_as_file, save_full_page_screenshot,
#       get_full_page_screenshot_as_png, get_full_page_screenshot_as_base64
