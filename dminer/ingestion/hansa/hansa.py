"""
The hansa parser module provides functionality for parsing scraped content
and passing it to the appropriate datastore interface.
"""
import json
import re
import os
import logging
import datetime
from bs4 import BeautifulSoup

import dminer.ingestion.helpers
from dminer.ingestion.base.parser import BaseParser
from dminer.ingestion.base.exceptions import DataStoreNotSpecifiedError


class HansaParser(BaseParser):
    """
    The `dminer.ingestion.hansa.HansaParser` controls the parsing logic
    for html pages and objects that are have been saved or scraped.
    """
    def __init__(self, datastore=None):

        self.datastore = datastore
        self.datastore_name = datastore.__class__.__name__.lower()
        self.logger = logging.getLogger(__name__)

    def store_elasticsearch(self, item):
        """
        Stores the given item in the elasticsearch database specified by
        the datastore.
        """
        self.datastore.create(
            index="dminer-hansa-{date}".format(
                date=datetime.datetime.strptime(
                    item["timestamp"], "%Y:%m:%d %H:%M:%S"
                ).date().strftime("%Y-%m-%d")
            ),
            doc_type="hansa_listing",
            body=item
        )

    def store(self, item):
        """
        Stores a given item to the datastore. If the datastore is None, an
        error will be raised
        (`dminer.ingestion.base.exceptions.DataStoreNotSpecifiedError`).
        """
        if isinstance(self.datastore, type(None)):
            raise DataStoreNotSpecifiedError("A datastore must be present in order to store a parsed result.")

        if self.datastore_name == "elasticsearchinterface":
            self.store_elasticsearch(item)

    def extract_listings(self, bs_obj, timestamp):
        """
        Extracts each hansa listing from the given `bs_obj` (`bs4.BeautifulSoup`)
        object. The listings will then be associated to the passed `timestamp`.
        Listings are then yielded (as this is a generator function).
        """
        # Each of the listings has it's own container with all relevant
        # information (row-item class tagged div elements).
        listing_containers = bs_obj.find_all("div", class_="row-item")

        for listing_container in listing_containers:
            # Define the item for this listing
            item = {
                "market_name": "Hansa"
            }

            item_details_container = listing_container.find(
                "div", class_="item-details"
            )
            user_details_container = listing_container.find(
                "div", class_="user-details"
            )
            listing_price_container = listing_container.find(
                "div", class_="listing-price"
            )

            # Parse the listing general details
            item["listing_name"] = item_details_container.find("a").text
            item["listing_views"] = int(
                listing_container.find(
                    "div", class_="text-muted text-center"
                ).find("small").text.split(" ")[1]
            )

            # Parse the listing pricing details
            item["listing_price_usd"] = float(
                listing_price_container.find("strong").text.split(" ")[1].replace(",", "")
            )
            item["listing_price_btc"] = float(
                listing_price_container.find("span", class_="text-muted").text
            )

            # Parse the vendor details
            item["vendor_name"] = user_details_container.find("a").text

            item["vendor_positive_reviews"] = int(
                user_details_container.find(
                    "strong", class_="fb-pos"
                ).text.lstrip("+")
            )
            item["vendor_negative_reviews"] = int(
                # We have to pull it out of REPR because of broken unicode
                user_details_container.find(
                    "strong", class_="fb-neg"
                ).string.replace(u'\N{MINUS SIGN}', '')
            )

            item["vendor_level"] = int(
                user_details_container.find(
                    "span", class_="label"
                ).text.strip().split(" ")[1].replace(",", "")
            )

            item["timestamp"] = timestamp
            print item
            # Yield the item as an entry
            yield item

    def parse(self,
              directory=None, directory_filename_pattern=None,
              scrape_results=None, **kwargs):
        """
        When ingesting from a directory if a `directory_filename_pattern` is
        not specified, the fetched files can be controlled through the use of
        the environment variable:

            DMINER_HANSA_PARSER_FILENAME_FORMAT

        For example, on a linux host you can perform:

            export DMINER_HANSA_PARSER_FILENAME_FORMAT=".*(?P<market_name>hansa)_(?P<market_category>.*)_(?P<month>\d\d)_(?P<day>\d\d)_(?P<year>\d\d).html"
        """
        if directory:
            file_pattern = os.environ.get(
                "DMINER_HANSA_PARSER_FILENAME_FORMAT",
                ".*(?P<market_name>hansa)_(?P<market_category>[a-zA-Z]*)_(?P<month>([0-9]{1,2}))_(?P<day>([0-9]{1,2}))_(?P<year>([0-9]{1,4}))_(?P<page>[0-9]{1,2}).html"
            ) if not directory_filename_pattern else directory_filename_pattern

            files = dminer.ingestion.helpers.get_files(directory)
            for filename in list(f for f in files if re.match(file_pattern, f)):
                match = re.match(file_pattern, filename)
                timestamp = dminer.ingestion.helpers.build_filename_timestamp(match)
                with open(filename, 'rb') as f:
                    soup = BeautifulSoup(f, 'html.parser')
                    for listing in self.extract_listings(soup, timestamp):
                        self.store(listing)

        elif scrape_results:
            for html_obj in scrape_results:
                soup = BeautifulSoup(html_obj, 'html.parser')
                timestamp = datetime.datetime.now().strftime("%Y:%m:%d %H:%M:%S")
                for listing in self.extract_listings(soup, timestamp):
                    self.store(listing)
