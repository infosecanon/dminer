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

	def save_file(self, directory, file_name, file_contents):
		if os.path.exists(directory):
			with open(os.path.join(directory, file_name), "wb") as f_obj:
				f_obj.write(file_contents)
		else:
			raise Exception("Directory was not found.")

	def get_urls_from_file(self, file_path):
		urls = []

		if os.path.exists(file_path):
			with open(file_path, "r") as f_obj:
				for line in f_obj:
					urls.append(line)
		else:
			raise Exception("URL file not found.")

		return urls

	def get_dynamic_urls(self):
		urls = []
		return urls

	def bypass_captcha(self, captcha_element, crop_dim):
		# Uses a temporary file so that we do not have to deal with cleanup
		temp_screenshot = tempfile.NamedTemporaryFile()
		# Open the screenshot and crop to captcha
		screenshot_image = Image.open(StringIO(self.selenium_driver.get_screenshot_as_base64().decode("base64")))
		screenshot_image = screenshot_image.crop(crop_dim)
		# Write the captcha out to disk
		screenshot_image.save(temp_screenshot.name, "png", quality=90)

		self.logger.info("Requesting deathbycaptcha solution...")
		try:
			captcha = self.dbc_client.decode(temp_screenshot.name, 200)
		except deathbycaptcha.AccessDeniedException:
			self.logger.error("Login problems, banned?")
			raise

		if captcha:
			captcha_id = captcha["captcha"]
			captcha_text = captcha["text"]
			# Enter the captcha
			input_element = self.selenium_driver.find_element_by_name(captcha_element)
			input_element.send_keys(captcha_text)
		# Done with the screenshot, will close handle and delete file
		temp_screenshot.close()

	def perform_login(self, username, password):
		self.logger.info("Requesting login page.")
		self.selenium_driver.get(
			"{onion_url}/login.php".format(
				onion_url=self.onion_url
			)
		)
		while "Login" in self.selenium_driver.title:
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
		# Get past DDOS protection and log in.
		self.logger.info("Attempting to log in.")
		self.perform_login(self.ab_username, self.ab_password)
		self.logger.info("Log in successful.")

		# If we are getting urls from a file, grab them now, otherwise, empty list
		self.logger.info("Fetching urls.")
		scrape_urls = self.get_urls_from_file(self.url_file) if self.url_file else self.get_dynamic_urls()
		self.logger.info("Urls fetched.")
		# Iterate the pulled URLS either from the file or from the dynamic pages
		for url in scrape_urls:
			self.logger.info("Attempting to scrape %s" % url)
			with dminer.sinks.helpers.wait_for_page_load(self.selenium_driver):
				self.selenium_driver.get(url)
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
					self.save_file(self.save_to_directory, file_name, file_contents)
					self.logger.info("Current page has been saved.")
				else:
					raise Exception("Unable to save scrape to file.")
				# Yield file contents for passing to the parser
				yield file_contents

			else:
				# Yield the file contents for passing to the parser
				yield file_contents
