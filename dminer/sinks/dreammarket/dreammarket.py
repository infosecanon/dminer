"""
TODO: DOC
"""
import urlparse
import platform
import time
import os

from datetime import datetime
from PIL import Image

import dminer.sinks.helpers
from dminer.lib import deathbycaptcha

class DreammarketSink(object):
	def __init__(self, *args, **kwargs):
		self.datastore = kwargs.get('datastore', None)
		self.selenium_driver = helpers.launch_selenium_driver()


		self.categories = {
			"cat136": "ce",
			"cat135": "c",
			"cat131": "hs",
			"cat118": "s",
			"cat117": "sec",
			"cat147": "pd",
			"cat114": "h",
			"cat108": "d"
		}

	def save_to_directory(self, directory, file_name, file_contents):
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

	def bypass_captcha(self, captcha_element, crop_dim):
		imageName = datetime.now().strftime('%m-%d-%H-%M-%S')
		# Get the screenshot of the web page so that we can crop to the captcha
		# TODO: DO I REALLY FUCKING WORK
		self.selenium_driver.get_screenshot_as_file('temp.png')
		# Open the screenshot and crop to captcha
		temp = Image.open("temp.png")
		#temp = temp.crop( (145,130,305,205) )
		temp = temp.crop(crop_dim)

		# Write the captcha out to disk
		imagefile = open(str(imageName+"-bypass-captcha.png"), 'wb')
		try:
			temp.save(imagefile, "png", quality=90)
			imagefile.close()
		except:
			print "Cannot save user image"
			raise
		# Remove the temporary PNG used to get past the captcha
		os.remove('temp.png')

		#now for the dbc part, please dont public this login
		client = deathbycaptcha.SocketClient(os.environ.get("DMINER_DBC_ACCESS_KEY", None), os.environ.get("DMINER_DBC_SECRET_KEY", None))
		try:
			#balance = client.get_balance()

			# Put your CAPTCHA file name or file-like object, and optional
			# solving timeout (in seconds) here:
			captcha = client.decode(imageName+"-bypass-captcha.png", 200)
			if captcha:
				captchaId = captcha["captcha"]
				text = captcha["text"]

				#type it in!
				inputElement = self.selenium_driver.find_element_by_name(captcha_element)
				inputElement.send_keys(text)
				time.sleep(10)
				if "DDoS Protection" in self.selenium_driver.title:
					print "Reporting bad captcha: " + str(captchaId)
					client.report(captchaId)
		except deathbycaptcha.AccessDeniedException:
			print "Login problems, banned?"
			raise

	def perform_login(self, username, password):
		self.selenium_driver.get("http://lchudifyeqm4ldjj.onion/")

		imageName = datetime.now().strftime('%m-%d-%H-%M-%S')

		#---- Known Bug ----#
		# Once the captcha fails once the captcha box moves down the page
		# due to the warning, thus DBC doesnt get the correct png to
		# interpret captcha. Check crop dimensions (crop_dim).

		# Determine if the page sent us to the DDoS pg or main pg
		while "DDoS Protection" in self.selenium_driver.title:
			crop_dim = (145,130,305,205)
			self.bypass_captcha("answer", crop_dim)
			# Submit the form
			self.selenium_driver.find_element_by_name("answer").submit()


		time.sleep(10)

		while "Login" in self.selenium_driver.title:
			print datetime.now()
			crop_dim = (250,380,450,450)

			inputElement = self.selenium_driver.find_element_by_name("Username")
			inputElement.send_keys(username)

			inputElement = self.selenium_driver.find_element_by_name("password")
			inputElement.send_keys(password)

			self.bypass_captcha("captcha_code", crop_dim)

			self.selenium_driver.find_element_by_name("captcha_code").submit()
			time.sleep(5)
		time.sleep(10)

	def scrape(self, username=None, password=None,
		             from_file=None, save_directory=None,
		             **kwargs):

		# Get past DDOS protection and log in.
		self.perform_login(username, password)

		# If we are getting urls from a file, grab them now, otherwise, empty list
		# TODO: implement dynamic scraping
		scrape_urls = self.get_urls_from_file(from_file) if from_file else list()

		for url in scrape_urls:

			# Parses the URL into a URL object, and parses the query into a dictionary of key:value
			# For example: www.google.com/my/leet/page?param=lol&other_param=cats
			# is parsed into:
			# {
			#	"param": ["lol"]
			#	"other_param": ["cats"]
			# }
			parsed_url, parsed_query = helpers.parse_url(url)

			# Iterating through a list of categories so that we can find the category that the
			# URL contains. If there is no category, then... _shrug_
			category_found = None
			for category in self.categories.keys():
				if category in parsed_query:
					category_found = category
					break


			# Use the category to build the filename to save on disk
			if category_found:
				timenow = datetime.now().strftime('%m%d%H%M%S')
				timenow_year = datetime.now().strftime('%y')
				timenow_month = datetime.now().strftime('%m')
				timenow_day = datetime.now().strftime('%d')
				timenow_second = datetime.now().strftime('%d')
				file_name = "dreammarket_" + category_found + '_' + timenow_month + '_' + timenow_day + '_' + timenow_year + '_' + timenow_second + ".html"
			else:
				# TODO: Fix the broham error
				raise Exception("Yo, not found broham")

			# Grab the page source for the given url
			try:
				file_contents = self.selenium_driver.page_source.encode('unicode_escape','ignore')
			except:
				file_contents = self.selenium_driver.page_source.decode('unicode_escape','ignore')

		if save_directory:
			self.save_to_directory(save_directory, file_name, file_contents)
		else:
			raise Exception("Oh shit waddup")
