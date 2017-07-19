"""
The dreammarket sink module provides functionality for scraping content from the
alphabay site, as well as passing it to the appropriate ingestion interface,
and saving scrapes for later processing.
"""
import time
import os
import logging
import requests
import random
import copy
import urllib
import numpy
import cv2

from datetime import datetime
from bs4 import BeautifulSoup

import dminer.sinks.helpers
from dminer.lib import deathbycaptcha


class DreammarketSink(object):
    """
    The alphabay sink provides functionality for scraping, saving, and
    ingesting content from the alphabay site.
    """
    def __init__(self, dreammarket_username, dreammarket_password,
                 dbc_access_key, dbc_secret_key,
                 url_file=None, save_to_directory=None,
                 onion_url="http://lchudifyeqm4ldjj.onion",
                 request_interval=15, request_retries=5,
                 request_timeout=5, category="security & hosting"):

        # Set DreamMarket credentials for login
        self.dreammarket_username = dreammarket_username
        self.dreammarket_password = dreammarket_password

        # Specify the url file to pull urls from
        self.url_file = url_file

        # Specify the directory to save scrapes to
        self.save_to_directory = save_to_directory

        # Bootstrap the requests session
        self.requests_session = requests.Session()

        # Set the interval between requests
        self.request_interval = request_interval

        # Set the number of attempts to make on a URL that is being redirected
        self.retry_attempts = request_retries

        # Set the request timeout on a URL
        self.request_timeout = request_timeout

        # Bootstrap deathbycaptcha client with supplied credentials
        self.dbc_client = deathbycaptcha.SocketClient(
            dbc_access_key, dbc_secret_key
        )

        # Create an instance of logging under the module's namespace
        self.logger = logging.getLogger(__name__)

        # The onion url
        self.onion_url = onion_url

        # Set the category to scrape
        self.category = category

    def get_categories(self, categories, path, depth, scope=""):
        """
        This method returns a mapping of category names to category URL's.
        It is built by requesting the index page of the market, and parsing
        the HTML to extract all of the categories and build a dictionary
        mapping of category hierarchy to category URL.
        """
        self.logger.info(
            "Getting categories from {path} by depth {depth} under scope {scope}".format(
                path=path,
                depth=depth,
                scope=scope
            )
        )
        # We request the homepage so that we can get the top-level FRC ids.
        page, request_success = self.perform_request(
            "{onion_url}{path}".format(
                onion_url=self.onion_url,
                path=path
            )
        )
        if not request_success:
            raise Exception(
                "Unable to request the {path} route to fetch categories.".format(
                    path=path
                )
            )
        # Parse the page and yield the categories for this level
        parsed_page = BeautifulSoup(
            page.text.encode("UTF-8"), "html.parser"
        )
        for category_element in parsed_page.find_all("div", class_="depth%s" % str(depth)):
            # Remove whitespace and replace spaces with underscores
            clean_category = "_".join(category_element.text.strip().split()[:-1]).lower()
            category = "{scope}{category}".format(
                scope="%s." % scope if not scope == "" else scope,
                category=clean_category
            )
            categories[category] = category_element.find("a")["href"].split("=")[-1]
            self.logger.info(
                "Fetching subcategories of {category}".format(
                    category=category
                )
            )
            # Find all categories under this category
            self.get_categories(
                categories,
                "?category=%s" % str(categories[category]),
                depth + 1,
                scope=category
            )

    def get_dynamic_urls(self):
        """
        This method provides URLs to scrape based off of the links scraped off
        of the page (specifically categories).
        """
        urls = []

        # We pull the categories so that we can fetch the start/stop page URLS
        category_dict = {}
        categories = self.get_categories(category_dict, "/", 0)
        print category_dict

        return urls

    def process_captcha(self, image):
        """
        TODO: DOC
        """
        cv2_img = cv2.cvtColor(numpy.array(image), cv2.COLOR_BGR2GRAY)

        # Find the threshold of the image so that we can identify contours.
        ret, thresh = cv2.threshold(
            cv2_img,
            127,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C
        )
        # Find the contours of the image
        _, contours, hierarchy = cv2.findContours(
            thresh,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        # Find the largest contour in the image with 4 points. This is the
        # rectangle that is required to crop to for the captcha.
        largest_contour = None
        for contour in contours:
            if (len(cv2.approxPolyDP(contour, 0.1*cv2.arcLength(contour, True), True)) == 4) and (2500 < cv2.contourArea(contour) < 4000):
                if isinstance(largest_contour, type(None)):
                    largest_contour = contour
                    continue
                if cv2.contourArea(contour) > cv2.contourArea(largest_contour):
                    largest_contour = contour
        # If we don't have a matching contour, don't try to crop and such
        if isinstance(largest_contour, type(None)):
            return None

        # If we do have a matching contour, build the rectangle
        crop_x, crop_y, crop_width, crop_height = cv2.boundingRect(
            largest_contour
        )
        # Crop down to the contour rectangle
        image = image.crop(
            (
                crop_x,
                crop_y,
                crop_x + crop_width,
                crop_y + crop_height
            )
        )
        return image

    def perform_login(self, username, password):
        """
        This method accesses the login page of the alphabay market, and
        proceeds to enter credentials and bypass the captcha on the login page.
        It will perform these actions until the login page is successfully
        bypassed.
        """
        selenium_driver = dminer.sinks.helpers.launch_selenium_driver()

        self.logger.info("Requesting login page.")
        with dminer.sinks.helpers.wait_for_page_load(selenium_driver):
            selenium_driver.get(
                "{onion_url}".format(
                    onion_url=self.onion_url
                )
            )

        # This is a special codeblock custom to DM to check if still on login pg
        while "login" in selenium_driver.title.lower():
            with dminer.sinks.helpers.wait_for_page_load(selenium_driver):
                selenium_driver.get(
                    "{onion_url}".format(
                        onion_url=self.onion_url
                    )
                )
            captcha_text = dminer.sinks.helpers.solve_captcha(
                selenium_driver,
                self.dbc_client,
                selenium_driver.find_element_by_xpath(
                    "//img[@alt='Captcha']"
                ),
                preprocessor=self.process_captcha
            )
            if captcha_text:
                self.logger.info(
                    "Attempting captcha solution with text: {captcha_text}".format(
                        captcha_text=captcha_text
                    )
                )
                # Enter the captcha
                selenium_driver.find_element_by_xpath(
                    "//input[@title='Captcha, case sensitive']"
                ).send_keys(captcha_text)
                # Enter the username
                input_element = selenium_driver.find_elements_by_xpath(
                    "//input[@value='' or @value='%s' and @type='text']" % username
                )[0]
                input_element.send_keys(username)
                # Enter the password
                input_element = selenium_driver.find_elements_by_xpath(
                    "//input[@value='' and @type='password']"
                )[0]
                input_element.send_keys(password)
                with dminer.sinks.helpers.wait_for_page_load(selenium_driver):
                    # Submit the form
                    selenium_driver.find_element_by_xpath(
                        "//input[@value='Login']"
                    ).click()
            else:
                self.logger.warn(
                    "Rerolling page to get new captcha."
                )

        # Go to the root and wait for the page to load so we can force the
        # session to stabilize
        self.logger.info("Stabilizing session.")
        with dminer.sinks.helpers.wait_for_page_load(selenium_driver):
            selenium_driver.get(self.onion_url)
        # Move into a headless session, since we bypassed DDOS/Login
        self.convert_headless(selenium_driver)

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
                "Host": "lchudifyeqm4ldjj.onion",
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
        This method saves a response to the instance specified directory,
        with a filename based on the time of saving and the category of the
        response.
        """
        current_time = datetime.now().strftime('%m_%d_%y_%H_%M_%S')
        file_name = "dreammarket_{category}_{timestamp}.html".format(
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

    def perform_request(self, url):
        """
        This method performs a request and returns the request object. It
        has various checks based on the instance settings, such as verifying
        that the user is signed in, performing login when the user becomes
        deauthenticated, and handling request timeout/interval/redirections.
        """
        response_success = False
        retry_attempts = self.retry_attempts
        # Pull down the page source into `response.text`
        self.logger.info("Requesting: %s" % url)
        while retry_attempts > 0:
            # Sleep for a random amount in between attempts, to prevent looking
            # like a bot.
            sleep_time = random.randrange(0, self.request_interval)
            self.logger.info("Sleeping thread for %is" % sleep_time)
            time.sleep(sleep_time)
            # Perform the request, without following redirects. If we are
            # redirected, then we need to make sure we handle it correctly,
            # as it could be to a login/ddos page, or to the home page.
            try:
                response = self.requests_session.get(
                    url,
                    allow_redirects=False,
                    timeout=self.request_timeout
                )
            except requests.exceptions.ConnectionError:
                self.logger.error("Request timeout, retrying.")
                continue

            # If the response status is 200, then we are fine to exit early
            if response.status_code == 200:
                return response, True
            # If the response status is 302, then we were being redirected.
            elif response.status_code == 302:
                # If we were being redirected to the login page, we will
                # reauthenticate.
                if "login" in response.headers["Location"].lower():
                    self.perform_login(
                        self.dreammarket_username, self.dreammarket_password
                    )
                # We fail hard if we don't know where we are being redirected
                # to, since this is not an expected condition.
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
        This method performs the actual scraping of the Dream Market site, which
        includes the fetching of URLS to be processed, requests made to the
        site, as well as saving the scrapes to a directory for later ingestion,
        or yielding them to the ingestion point.

        Note: This function is a generator, and must be itereated to invoke
        processing.
        """
        # Get past DDOS protection and log in.
        self.logger.info("Attempting to log in.")
        # Get an Alphabay session through selenium due to the captcha
        self.perform_login(
            self.dreammarket_username,
            self.dreammarket_password
        )

        while True:
            # If we are getting urls from a file, grab them now, otherwise,
            # empty list
            self.logger.info("Fetching urls.")
            scrape_urls = \
                dminer.sinks.helpers.get_urls_from_file(self.url_file) \
                if self.url_file \
                else self.get_dynamic_urls()
            self.logger.info("Fetched %s urls." % str(len(scrape_urls)))

            for url in scrape_urls:
                response, response_success = self.perform_request(url)
                if response_success:
                    # Save the file to disk, if the flag is set to do so
                    if self.save_to_directory:
                        # Save the file out
                        self.save_out(url, response.text.encode("UTF-8"))
                    yield response.text.encode("UTF-8")
            if not daemon:
                break
