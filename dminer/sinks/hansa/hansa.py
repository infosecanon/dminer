"""
TODO: DOC
"""
import time
import os
import logging
import requests
import random
import copy
import urllib

from datetime import datetime
from bs4 import BeautifulSoup

import dminer.sinks.helpers

from dminer.lib import deathbycaptcha


class HansaSink(object):
    """
    TODO: DOC
    """
    def __init__(self,
                 dbc_access_key, dbc_secret_key,
                 onion_url="http://hansamkt2rr6nfg3.onion",
                 url_file=None, save_to_directory=None,
                 request_interval=15, request_retries=5,
                 request_timeout=5, category="security & hosting"):

        # Set the URL file to pull urls from
        self.url_file = url_file

        # Specify the directory to save scrapes to
        self.save_to_directory = save_to_directory

        # Set the onion url to scrape from
        self.onion_url = onion_url

        # Bootstrap deathbycaptcha client with supplied credentials
        self.dbc_client = deathbycaptcha.SocketClient(
            dbc_access_key, dbc_secret_key
        )

        # Set the category to scrape from
        self.category = category

        # Set the request interval
        self.request_interval = request_interval

        # Set the request retries
        self.request_retries = request_retries

        # Set the request timeout
        self.request_timeout = request_timeout

        # Bootstrap the requests session
        self.requests_session = requests.Session()
        # Set up the HTTP Adapter to change retry settings
        self.requests_session.mount(
            self.onion_url,
            requests.adapters.HTTPAdapter(
                max_retries=request_retries
            )
        )
        # Masquerade as Firefox
        self.requests_session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:53.0) Gecko/20100101 Firefox/53.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Upgrade-Insecure-Requests": "1",
                "Cache-Control": "max-age=0"
            }
        )

        # Create an instance of logging under the module's namespace
        self.logger = logging.getLogger(__name__)

    def get_categories(self):
        """
        TODO: DOC
        """
        categories = {}

        self.logger.info("Fetching index for categories.")
        # Request the homepage so that we can get the top-level categories
        home_page, request_success = self.perform_request(self.onion_url)
        if not request_success:
            raise Exception(
                "Unable to request the index page to fetch categories."
            )

        parsed_home = BeautifulSoup(
            home_page.text.encode("UTF-8"), "html.parser"
        )

        self.logger.info("Parsing index for category URLS.")
        # Iterate through the category links on the homepage to build the
        # mapping between the category names and urls.
        for category_link in parsed_home.find_all("a", class_="list-group-item"):
            dirty_category_name = category_link.text.lower().strip()
            # Strip out the number of listings (which is the last space
            # separated  element of each category)
            clean_category_name = " ".join(dirty_category_name.split(" ")[:-1])
            category_url = "{onion_url}{relative_path}".format(
                onion_url=self.onion_url,
                relative_path=category_link["href"]
            )
            categories[clean_category_name] = category_url
        self.logger.info(categories)
        return categories

    def get_dynamic_urls(self):
        """
        TODO: DOC
        """
        urls = []

        # Pull the categories so we can fetch the start/stop page URLS
        categories = self.get_categories()
        # Try to pull the category name from the category mapping, if it exists
        try:
            category_url = categories[self.category]
        except KeyError:
            raise Exception("The specified market category was not found.")

        category_page, request_success = self.perform_request(category_url)
        if not request_success:
            raise Exception(
                "Unable to request the category page ({category})".format(
                    category=self.category
                )
            )

        self.logger.info(
            "Parsing category page ({category}) for page URLS.".format(
                category=self.category
            )
        )
        parsed_category_page = BeautifulSoup(
            category_page.text.encode("UTF-8"), "html.parser"
        )

        # We find the pagination UL because the list elements inside it are
        # the category elements.
        pagination_list = parsed_category_page.find("ul", class_="pagination")
        pagination_list_elements = pagination_list.find_all("li")

        # Pull the last page button from the UL so we can parse the relative
        # path and pull the total number of pages.
        last_page_list_element = pagination_list_elements[-1]
        last_page_link = last_page_list_element.find("a")
        last_page_relative_path = last_page_link["href"]

        # Get the category ID so that we can build the pages for this category
        category_id = int(last_page_relative_path.split("/")[2])
        # Get the total number of pages so that we can iterate them
        total_pages = int(last_page_relative_path.split("/")[3])

        for page_num in range(1, total_pages + 1):
            urls.append(
                "{onion_url}/{relative_path}".format(
                    onion_url=self.onion_url,
                    relative_path="category/{category_id}/{page_num}/".format(
                        category_id=category_id,
                        page_num=page_num
                    )
                )
            )

        return urls

    def save_out(self, url, response):
        """
        TODO: DOC
        """
        current_time = datetime.now().strftime("%m_%d_%y_%H_%M_%S")
        file_name = "hansa_{category}_{timestamp}.html".format(
            category=self.category,
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

    def convert_headless(self, selenium_driver):
        """
        This method converts the session stored in the selenium driver into
        the instance's request session. It does so by disgarding the old
        session object for this instance and replacing it with a new requests
        session with the selenium session transfered into it. This method
        also closes the selenium driver once the session has been cloned.
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

    def perform_ddos_prevention(self):
        """
        TODO: DOC
        """
        # Spawn selenium so that we can fetch the challenge page.
        selenium = dminer.sinks.helpers.launch_selenium_driver()
        # Fetch the challenge page so we can update our session with the
        # cookie that allows us to escape the challenge sandbox.
        selenium.get("{onion_url}/challenge/".format(onion_url=self.onion_url))

        # Identify the form so that we can isolate our search.
        captcha_form = selenium.find_element_by_class_name("form-group")
        # Identify the image within the form (this is the captcha).
        captcha_image = captcha_form.find_element_by_tag_name("img")
        # Identify the text entry within the form (this is where the response
        # is entered).
        captcha_entry = captcha_form.find_element_by_id("sec")

        # Solve the captcha using the elements we have isolated from the form.
        captcha_text = dminer.sinks.helpers.solve_captcha(
            selenium,
            self.dbc_client,
            captcha_image
        )
        captcha_entry.send_keys(captcha_text)

        with dminer.sinks.helpers.wait_for_page_load(selenium):
            selenium.find_element_by_tag_name("button").click()

        # Move into a headless session and close the selenium driver
        self.convert_headless(selenium)

    def perform_request(self, url):
        """
        TODO: DOC
        """
        response_success = False
        retry_attempts = self.request_retries

        self.logger.info("Rquesting %s" % url)
        while retry_attempts > 0:
            sleep_time = random.randrange(0, self.request_interval)
            self.logger.info("Sleeping thread for %is" % sleep_time)
            time.sleep(sleep_time)

            try:
                response = self.requests_session.get(
                    url,
                    allow_redirects=False,
                    timeout=self.request_timeout
                )
            except requests.exceptions.ConnectionError:
                self.logger.error("Request timeout, retrying.")
                continue

            if response.status_code == 200:
                return response, True
            elif response.status_code == 302:
                self.logger.info(
                    "Redirection from {original_url} to {redirect_url}".format(
                        original_url=url,
                        redirect_url=response.headers["Location"]
                    )
                )
                if "challenge" in response.headers["Location"]:
                    self.perform_ddos_prevention()
                retry_attempts -= 1
            else:
                raise Exception(
                    "Redirection from {original_url} to {redirect_url}".format(
                        original_url=url,
                        redirect_url=response.headers["Location"]
                    )
                )
        return response, False

    def scrape(self, daemon=False):
        """
        TODO: DOC
        """
        while True:
            self.logger.info("Fetching urls.")
            scrape_urls = \
                dminer.sinks.helpers.get_urls_from_file(self.url_file) \
                if self.url_file \
                else self.get_dynamic_urls()
            self.logger.info("Fetched %s urls." % str(len(scrape_urls)))

            for url in scrape_urls:
                response, response_success = self.perform_request(url)
                if response_success:
                    if self.save_to_directory:
                        self.save_out(url, response.text.encode("UTF-8"))
                    yield response.text.encode("UTF-8")
            if not daemon:
                break
