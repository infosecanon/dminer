"""
The alphabay sink module provides functionality for scraping content from the
alphabay site, as well as passing it to the appropriate ingestion interface,
and saving scrapes for later processing.
"""
import urlparse
import time
import os
import tempfile
import logging
import requests

from datetime import datetime
from PIL import Image
from StringIO import StringIO
from bs4 import BeautifulSoup

import dminer.sinks.helpers
from dminer.lib import deathbycaptcha


class AlphabaySink(object):
    """
    The alphabay sink provides functionality for scraping, saving, and
    ingesting content from the alphabay site.
    """
    def __init__(self, ab_username, ab_password,
                 dbc_access_key, dbc_secret_key,
                 url_file=None, save_to_directory=None,
                 onion_url="http://pwoah7foa6au2pul.onion",
                 request_interval=0.5):

        # Set Alphabay credentials for login
        self.ab_username = ab_username
        self.ab_password = ab_password

        # Specify the url file to pull urls from
        self.url_file = url_file

        # Specify the directory to save scrapes to
        self.save_to_directory = save_to_directory

        # Bootstrap the requests session
        self.requests_session = requests.Session()

        # Set the interval between requests
        self.request_interval = request_interval

        # Bootstrap deathbycaptcha client with supplied credentials
        self.dbc_client = deathbycaptcha.SocketClient(
            dbc_access_key, dbc_secret_key
        )

        # Create an instance of logging under the module's namespace
        self.logger = logging.getLogger(__name__)

        # The onion url
        self.onion_url = onion_url

        self.categories = {
            "cat114": "bm",
            "cat115": "e",
            "cat116": "ek",
            "cat117": "ss",
            "cat119": "o1",
            "cat124": "o2",
            "cat86": "ce"
        }

    def get_dynamic_urls(self):
        """
        This method provides URLs to scrape based off of the links scraped off
        of the page (specifically categories).
        """
        urls = []
        return urls

    def perform_login(self, username, password):
        """
        This method accesses the login page of the alphabay market, and
        proceeds to enter credentials and bypass the captcha on the login page.
        It will perform these actions until the login page is successfully
        bypassed.
        """
        selenium_driver = dminer.sinks.helpers.launch_selenium_driver()

        self.logger.info("Requesting login page.")
        selenium_driver.get(
            "{onion_url}/login.php".format(
                onion_url=self.onion_url
            )
        )

        while "login" in selenium_driver.title.lower():
            # Enter the username
            input_element = selenium_driver.find_element_by_name("user")
            input_element.send_keys(username)
            # Enter the password
            input_element = selenium_driver.find_element_by_name("pass")
            input_element.send_keys(password)
            # Enter the captcha
            dminer.sinks.helpers.solve_captcha(
                selenium_driver,
                self.dbc_client,
                selenium_driver.find_element_by_id("captcha"),
                selenium_driver.find_element_by_name("captcha_code")
            )
            # Submit the form
            with dminer.sinks.helpers.wait_for_page_load(selenium_driver):
                selenium_driver.find_element_by_name("captcha_code").submit()

        # Go to the root and wait for the page to load so we can force the
        # session to stabilize
        self.logger.info("Stabilizing session.")
        with dminer.sinks.helpers.wait_for_page_load(selenium_driver):
            selenium_driver.get(
                "{onion_url}/index.php".format(onion_url=self.onion_url)
            )
        # Move into a headless session, since we bypassed DDOS/Login
        self.convert_headless(selenium_driver)

    def perform_ddos_prevention(self, username, password):
        """
        This method allows for the bypassing of the ddos protection page. It
        will continue attempting to bypass it until it succeeds.
        """
        while True:
            if "ddos" in self.selenium_driver.title.lower():
                # Enter the username
                input_element = self.selenium_driver.find_element_by_name("user")
                input_element.send_keys(username)
                # Enter the password
                input_element = self.selenium_driver.find_element_by_name("pass")
                input_element.send_keys(password)
                # Enter the captcha
                dminer.sinks.helpers.solve_captcha(
                    self.selenium_driver,
                    self.dbc_client,
                    self.selenium_driver.find_element_by_id("captcha"),
                    self.selenium_driver.find_element_by_name("captcha_code")
                )
                with dminer.sinks.helpers.wait_for_page_load(self.selenium_driver):
                    # Submit the form
                    self.selenium_driver.find_element_by_name("captcha_code").submit()
            else:
                break
        # Go to the root and wait for the page to load so we can force the
        # session to stabilize
        self.logger.info("Stabilizing session.")
        with dminer.sinks.helpers.wait_for_page_load(selenium_driver):
            selenium_driver.get(
                "{onion_url}/index.php".format(onion_url=self.onion_url)
            )
        # Move into a headless session, since we bypassed DDOS/Login
        self.convert_headless(selenium_driver, self.requests_session)

    def maybe_handle_bypass(self, response, url):
        """
        TODO: DOC
        """
        parsed_response = BeautifulSoup(response.content, "html.parser")
        if "login" in parsed_response.html.title.string.lower():
            self.perform_login(self.ab_username, self.ab_password)
            response = self.requests_session.get(url)
        elif "ddos" in parsed_response.html.title.string.lower():
            self.perform_ddos_prevention(self.ab_username, self.ab_password)
            response = self.requests_session.get(url)

        return response

    def convert_headless(self, selenium_driver):
        """
        TODO: DOC
        """
        # Create a requests session to populate with the new session created
        # in selenium.
        self.requests_session = requests.Session()
        self.requests_session.mount(
            self.onion_url, requests.adapters.HTTPAdapter(max_retries=5)
        )
        self.requests_session.headers.update(
            {
                "Host": "pwoah7foa6au2pul.onion",
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:53.0) Gecko/20100101 Firefox/53.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Upgrade-Insecure-Requests": "1",
                "Cache-Control": "max-age=0"
            }
        )

        # Clone the session headers from selenium into requests
        self.logger.info(
            "Cloning selenium session into python-requests session."
        )
        dminer.sinks.helpers.clone_selenium_session_to_requests(
            selenium_driver, self.requests_session
        )
        # Close the selenium instance, as it is no longer needed.
        self.logger.info("Closing selenium driver.")
        selenium_driver.close()

    def save_out(self, url, response):
        """
        TODO: DOC
        """
        # Parses the URL into a URL object, and parses the query into a
        # dictionary of key:value
        #
        # For example:
        # www.google.com/my/leet/page?param=lol&other_param=cats
        # is parsed into:
        # {
        #    "param": ["lol"]
        #    "other_param": ["cats"]
        # }
        parsed_url, parsed_query = dminer.sinks.helpers.parse_url(url)

        category_found = None
        for category in self.categories.keys():
            if category in parsed_query:
                category_found = category
                break

        if category_found:
            current_time = datetime.now().strftime('%m_%d_%y_%H_%M_%S')
            file_name = "alphabay_{category}_{timestamp}.html".format(
                category=category_found,
                timestamp=current_time
            )
            self.logger.info(
                "Saving {url} page to {disk_path}".format(
                    url=url,
                    disk_path=os.path.join(self.save_to_directory, file_name)
                )
            )
            dminer.sinks.helpers.save_file(
                self.save_to_directory,
                file_name, response
            )

    def scrape(self):
        """
        This method performs the actual scraping of the alphabay site, which
        includes the fetching of URLS to be processed, requests made to the
        site, as well as saving the scrapes to a directory for later ingestion,
        or yielding them to the ingestion point.

        Note: This function is a generator, and must be itereated to invoke
        processing.
        """
        # Get past DDOS protection and log in.
        self.logger.info("Attempting to log in.")
        # Get an Alphabay session through selenium due to the captcha
        self.perform_login(self.ab_username, self.ab_password)

        # If we are getting urls from a file, grab them now, otherwise, empty
        # list
        self.logger.info("Fetching urls.")
        scrape_urls = \
            dminer.sinks.helpers.get_urls_from_file(self.url_file) \
            if self.url_file \
            else self.get_dynamic_urls()

        for url in scrape_urls:
            # Sleep the thread to force maximum request interval of the
            # specified interval
            time.sleep(self.request_interval)
            # Pull down the page source into `response.text`
            self.logger.info("Requesting: %s" % url)
            response = self.requests_session.get(url)
            # Verify that the page is not a DDOS/Login page, and if it is,
            # bypass and fetch the URL
            response = self.maybe_handle_bypass(response, url)

            # Save the file to disk, if the flag is set to do so
            if self.save_to_directory:
                # Save the file out
                self.save_out(url, response.text.encode("UTF-8"))
            yield response.text.encode("UTF-8")
