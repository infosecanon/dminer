"""
TODO: DOC
"""
import urlparse
import time
import os
import tempfile
import logging

from datetime import datetime
from PIL import Image
from StringIO import StringIO

import dminer.sinks.helpers
from dminer.lib import deathbycaptcha


class AlphabaySink(object):
	def __init__(self, ab_username, ab_password,
					   dbc_access_key, dbc_secret_key,
					   url_file=None, save_to_directory=None,
					   onion_url="http://pwoah7foa6au2pul.onion"):

		# Set Alphabay credentials for login
		self.ab_username = ab_username
		self.ab_password = ab_password
		
		# Specify the url file to pull urls from
		self.url_file = url_file
		
		# Specify the directory to save scrapes to
		self.save_to_directory = save_to_directory
		
		# Spin up this instance sinks selenium instance
		self.selenium_driver = dminer.sinks.helpers.launch_selenium_driver()
		
		# Bootstrap deathbycaptcha client with supplied credentials
		self.dbc_client = deathbycaptcha.SocketClient(dbc_access_key, dbc_secret_key)
		
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
		urls = []
		return urls

	def perform_login(self, username, password):
		"""
		TODO: DOC
		"""
		self.logger.info("Requesting login page.")
		self.selenium_driver.get(
			"{onion_url}/login.php".format(
				onion_url=self.onion_url
			)
		)
		while "login" in self.selenium_driver.title.lower():
			with dminer.sinks.helpers.wait_for_page_load(self.selenium_driver):
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
				# Submit the form
				self.selenium_driver.find_element_by_name("captcha_code").submit()
	
	def perform_ddos_prevention(self, username, password):
		"""
		TODO: DOC
		"""
		while "ddos" in self.selenium_driver.title.lower():
			with dminer.sinks.helpers.wait_for_page_load(self.selenium_driver):
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
				# Submit the form
				self.selenium_driver.find_element_by_name("captcha_code").submit()

	def scrape(self):
		"""
		TODO: DOC
		"""
		# Get past DDOS protection and log in.
		self.logger.info("Attempting to log in.")
		self.perform_login(self.ab_username, self.ab_password)

		# If we are getting urls from a file, grab them now, otherwise, empty list
		self.logger.info("Fetching urls.")
		scrape_urls = dminer.sinks.helpers.get_urls_from_file(self.url_file) if self.url_file else self.get_dynamic_urls()
		# Iterate the pulled URLS either from the file or from the dynamic pages
		for url in scrape_urls:
			self.logger.info("Attempting to scrape %s" % url)
			with dminer.sinks.helpers.wait_for_page_load(self.selenium_driver):
				self.selenium_driver.get(url)
				# If we are asked to log in again, we log in again
				if "login" in self.selenium_driver.title.lower():
					self.perform_login()
				# If we are presented the ddos prevention page, bypass captcha
				# and credential request
				if "ddos" in self.selenium_driver.title.lower():
					self.perform_ddos_prevention()
				# Grab the page source for the given url
				file_contents = self.selenium_driver.execute_script("return document.documentElement.outerHTML").encode("UTF-8")

			# Parses the URL into a URL object, and parses the query into a dictionary of key:value
			# For example: www.google.com/my/leet/page?param=lol&other_param=cats
			# is parsed into:
			# {
			#	"param": ["lol"]
			#	"other_param": ["cats"]
			# }
			parsed_url, parsed_query = dminer.sinks.helpers.parse_url(url)

			if self.save_to_directory:
				# Iterating through a list of categories so that we can find the category that the
				# URL contains. If there is no category, then... _shrug_
				category_found = None
				for category in self.categories.keys():
					if category in parsed_query:
						category_found = category
						break

				if self.save_to_directory and category_found:
					current_time = datetime.now().strftime('%m_%d_%y_%H_%M_%S')
					file_name = "alphabay_{category}_{timestamp}.html".format(
						category=category_found,
						timestamp=current_time
					)
					self.logger.info("Saving current page to %s" % os.path.join(self.save_to_directory, file_name))
					dminer.sinks.helpers.save_file(self.save_to_directory, file_name, file_contents)
					self.logger.info("Current page has been saved.")
				else:
					raise Exception("Unable to save scrape to file.")
				yield file_contents
			else:
				yield file_contents
