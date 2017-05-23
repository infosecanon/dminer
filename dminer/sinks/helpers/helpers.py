import platform
import urlparse
import logging
import tempfile

from contextlib import contextmanager
from StringIO import StringIO
from PIL import Image

import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.proxy import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of


logger = logging.getLogger(__name__)

def launch_selenium_driver():
	"""
	TODO: DOC
	"""
	#Building the profile, setting the port equal to tor on localhost
	profile = webdriver.FirefoxProfile()
	profile.set_preference("network.proxy.type", 1)
	profile.set_preference("network.proxy.socks", "127.0.0.1")

	#Assuming tor port is default, 9050, if you are using another proxy, you can change socks_port to http_port and so forth
	profile.set_preference("network.proxy.socks_port", 9050)
	profile.set_preference("network.proxy.socks_remote_dns", True)
	profile.set_preference("javascript.enabled", False)
	#Tor Browser settings, to bypass fingerprinting
	profile.set_preference("places.history.enabled", False)
	profile.set_preference("privacy.clearOnShutdown.offlineApps", True)
	profile.set_preference("privacy.clearOnShutdown.passwords", True)
	profile.set_preference("privacy.clearOnShutdown.siteSettings", True)
	profile.set_preference("privacy.sanitize.sanitizeOnShutdown", True)
	profile.set_preference("signon.rememberSignons", False)
	profile.set_preference("network.cookie.lifetimePolicy", 2)
	profile.set_preference("network.dns.disablePrefetch", True)
	profile.set_preference("network.http.sendRefererHeader", 0)

	profile.update_preferences()

	#Setting the binary path for firefox, using platform for cross commpatibility, if you don't want to use platform remove platform and set the path manually
	if(platform.system()=='Windows'):
		binary = FirefoxBinary('C:\\Program Files (x86)\\Mozilla Firefox\\Firefox.exe')
	else:
		binary = FirefoxBinary('/usr/bin/firefox')

	logger.info("Launching Firefox.")
	driver = webdriver.Firefox(firefox_profile=profile)
	logger.info("Firefox launched.")
	driver.set_window_size(1000, 1000)

	return driver


def parse_url(url):
	"""
	TODO: DOC
	"""
	parsed_url = urlparse.urlparse(url)
	parsed_query = urlparse.parse_qs(parsed_url.query)
	return (parsed_url, parsed_query)

@contextmanager
def wait_for_page_load(driver, timeout=30):
	"""
	TODO: DOC
	"""
	while True:
		try:
			old_page = driver.find_element_by_tag_name('html')
			break
		except selenium.common.exceptions.NoSuchElementException:
			pass
	yield
	WebDriverWait(driver, timeout).until(
	    staleness_of(old_page)
	)


def solve_captcha(selenium_driver, dbc_instance, 
				  image_element, entry_element):
	"""
	TODO: DOC
	"""
	# Create a temporary file to store on-disk. Needed for use with DBC
	temp_captcha_file = tempfile.NamedTemporaryFile()
	
	# Needed to do the element cropping calculations
	image_element_location = image_element.location
	image_element_size = image_element.size
	
	# Save as base64 so that we can decode directly into a StringIO "file-like"
	# object for direct manipulation.
	captcha_image = Image.open(StringIO(selenium_driver.get_screenshot_as_png()))
	# Crop to the captcha image
	captcha_image = captcha_image.crop(
		(
			# left
			image_element_location['x'],
			# Top
			image_element_location['y'],
			# Right
			image_element_location['x'] + image_element_size['width'],
			# Bottom
			image_element_location['y'] + image_element_size['height']
		)
	)
	# Save the captcha to the temp file.
	captcha_image.save(temp_captcha_file.name, "png", quality=90)
	
	# Attempt to solve the captcha
	captcha_result = dbc_instance.decode(temp_captcha_file.name, 200)
	
	# Will close handle and delete file
	temp_captcha_file.close()
	
	# Pull the captcha text for entry and enter them
	entry_element.send_keys(captcha_result["text"])
	
	
	
	
	
	
