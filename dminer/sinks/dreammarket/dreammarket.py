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

    def get_categories(self):
        """
        This method returns a mapping of category names to category URL's.
        It is built by requesting the index page of the market, and parsing
        the HTML to extract categories for scraping.
        """
        categories = {}

        self.logger.info("Fetching index for categories.")
        # We request the homepage so that we can get the top-level FRC ids.
        home_page, request_success = self.perform_request(
            "{onion_url}/index.php".format(
                onion_url=self.onion_url
            )
        )

        if not request_success:
            raise Exception(
                "Unable to request the index page to fetch categories."
            )
        parsed_home = BeautifulSoup(
            home_page.text.encode("UTF-8"), "html.parser"
        )

        self.logger.info("Parsing index for category URLS.")
        # Iterate through the FRC ids to build the mapping between category
        # text names and urls.
        for category_link_element in parsed_home.find_all("a", class_="category"):
            category_name = category_link_element.text.lower().strip()
            category_url = "{onion_url}/{category_url}".format(
                onion_url=self.onion_url,
                category_url=category_link_element["href"]
            )
            categories[category_name] = category_url
        return categories

    def get_dynamic_urls(self):
        """
        This method provides URLs to scrape based off of the links scraped off
        of the page (specifically categories).
        """
        urls = []

        # We pull the categories so that we can fetch the start/stop page URLS
        categories = self.get_categories()

        # Try to pull the category name from our category mapping, if it exists
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

        # Find the last page button based on the last.png img tag's parent
        # element.
        last_page_button_img = parsed_category_page.find(
            "img",
            {
                "class": "std",
                "src": "images/last.png"
            }
        )
        if not last_page_button_img:
            raise Exception(
                "Unable to identify the last page image element."
            )

        # If the element exists, grab the parent element, since the parent is
        # what contains the relative path with the query parameters we are
        # looking for
        last_page_button_parent = last_page_button_img.parent
        if not last_page_button_parent:
            raise Exception(
                "Unable to identify the last page image element parent."
            )

        last_page_url = "{onion_url}/{last_page}".format(
            onion_url=self.onion_url,
            last_page=last_page_button_parent["href"]
        )

        last_page_url, last_page_params = dminer.sinks.helpers.parse_url(
            last_page_url
        )
        # Build the last page number so that we can iterate & build the pages
        # up to it
        last_page_number = int("".join(last_page_params["pg"]))

        for page_num in range(1, last_page_number + 1):
            page_params = copy.deepcopy(last_page_params)
            page_params["pg"] = [str(page_num)]
            # Flatten the parameters
            page_params = dict(
                (k, v[0]) for k, v in page_params.iteritems()
            )
            # Append the built URL
            urls.append(
                "{onion_url}{page_path}".format(
                    onion_url=self.onion_url,
                    page_path="{path}?{params}".format(
                        path=last_page_url.path,
                        params=urllib.urlencode(page_params)
                    )
                )
            )

        return urls
    
    def process_captcha(self, image):
        """
        TODO: DOC
        """
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
        selenium_driver.get(
            "{onion_url}".format(
                onion_url=self.onion_url
            )
        )


        # This is a special codeblock custom to DM to check if still on login pg
        while "login" in selenium_driver.title.lower():
            # Enter the username
            input_element = selenium_driver.find_elements_by_xpath("//input[@value='' and @type='text']")[0]
            input_element.send_keys(username)
            # Enter the password
            input_element = selenium_driver.find_elements_by_xpath("//input[@value='' and @type='password']")[0]
            input_element.send_keys(password)

            # Enter the captcha
            dminer.sinks.helpers.solve_captcha(
                selenium_driver,
                self.dbc_client,
                selenium_driver.find_element_by_xpath("//img[@alt='Captcha']"),
                selenium_driver.find_element_by_xpath("//input[@title='Captcha, case sensitive']"),
                preprocessor=self.process_captcha
            )
            raw_input("hello")
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

    def perform_ddos_prevention(self, dreammarket_username, dreammarket_password):
        """
        This method allows for the bypassing of the ddos protection page. It
        will continue attempting to bypass it until it succeeds.
        """
        self.logger.info("Performing DDOS prevention.")
        while True:
            if "ddos" in self.selenium_driver.title.lower():
                # Enter the username
                input_element = self.selenium_driver.find_element_by_name("user")
                input_element.send_keys(dm_username)
                # Enter the password
                input_element = self.selenium_driver.find_element_by_name("pass")
                input_element.send_keys(dm_password)
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
                # If we were being redirected to the DDOS prevention page,
                # we will perform the ddos prevention.
                elif "ddos" in response.headers["Location"].lower():
                    self.perform_ddos_prevention(
                        self.dreammarket_username, self.dreammarket_password
                    )
                # If it's neither the DDOS prevention page or the login page,
                # we know it's the index page, and that we need to try again
                # (if we have enough retry attempts left).
                elif "index" in response.headers["Location"].lower():
                    self.logger.error(
                        "Redirection from {original_url} to {redirect_url}".format(
                            original_url=url,
                            redirect_url=response.headers["Location"]
                        )
                    )
                    retry_attempts -= 1
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
        self.perform_login(self.dreammarket_username, self.dreammarket_password)

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
