from bs4 import BeautifulSoup
import re, os, logging, datetime, helpers

class DreammarketParser(object):
    """
    The DreammarketParser controls the parsing logic for html pages and objects
    passed to it. It results in the creation of
    """
    def __init__(self, datastore=None):
        """

        """
        self.datastore = datastore
        self.logger = logging.getLogger(__name__)

    def _store(self, item):
        """
        Stores a given item to the datastore. If the datastore is none, an
        error will be raised (`dminer.ingestion.dreammarket.DataStoreNotSpecifiedError`).
        """
        if isinstance(self.datastore, type(None)):
            raise DataStoreNotSpecifiedError("A datastore must be present in order to store a parsed result.")

        self.datastore.create(
            document=item,
            type="dreammarket_listing",
            parser="dreammarket"
        )

    def extract_listings(self, soup, timestamp):
        """
        Extracts each DreamMarket listing from the given `soup` variable
        (`bs4.BeautifulSoup`) object. The listings will then be associated to
        the passed `timestamp`. Each listing item is then yielded to the
        caller.

        It is notable that there is currently one situation in which a listing
        will be skipped, and that is if there is no `primary_div` found.
        """

        listings = soup.find_all("div", class_="around")
        for listing_element in listings:
            title_div = listing_element.find("div", class_="oTitle")
            primary_div = listing_element.find("div", class_="oOfferBody")
            if not primary_div:
                self.logger.info("skipping entry:" + repr(title_div.find("a").text.strip()) + "| Reason: No primary_div found.")
                continue

            listing_meta_div = primary_div.find("td", class_="oOfTextDetail")
            vendor_div = listing_meta_div.find("div", class_="oVendor")

            item = {}
            item["market_name"] = "DreamMarket"
            item["listing_name"] = title_div.find("a").text.strip()
            item["timestamp"] = timestamp

            item["listing_price"] = {
                # starting at 1 to avoid the bitcoin icon
                "BTC": float(listing_meta_div.find("div", class_="oPrice").text.strip()[1:]),
                "escrow": primary_div.find("div", class_="escrowBox").text
            }


            vendor_name = list(tag for tag in vendor_div.find_all("a") if tag["href"].startswith("./"))[0].text.strip()
            vendor_transactions = int(vendor_div.find("span", title="Successful transactions").text.lstrip("(").rstrip(")"))
            vendor_rating = vendor_div.find("span", class_="userRating")
            if vendor_rating:
                vendor_rating = float(vendor_rating.text.strip())
            else:
                vendor_rating = float(0)

            item["listing_vendor"] = {
                "name": vendor_name,
                "transactions": vendor_transactions,
                "rating": vendor_rating
            }

            yield item

    def parse(self, directory=None, scrape_results=None, **kwargs):
        """
        The fetched files can be controlled through the use of the environment
        variable:

            DMINER_DREAMMARKET_PARSER_FILENAME_FORMAT

        For example, on a linux host you can perform:

            export DMINER_DREAMMARKET_PARSER_FILENAME_FORMAT=".*(?P<market_name>dreammarket)_(?P<market_category>[a-zA-Z]*)_(?P<month>([0-9]{1,2}))_(?P<day>([0-9]{1,2}))_(?P<year>([0-9]{1,4}))_(?P<page>[0-9]{1,2}).html"

        which will extract the year, month, and day for use as a timestamp when
        indexing data into the datastore. It is notable that this pattern is
        matched, then passed to `dminer.ingestion.helpers.build_filename_timestamp`
        for building the timestamp for a given set of listings.
        """

        if directory:
            file_pattern = os.environ.get(
                "DMINER_DREAMMARKET_PARSER_FILENAME_FORMAT",
                ".*(?P<market_name>dreammarket)_(?P<market_category>[a-zA-Z]*)_(?P<month>([0-9]{1,2}))_(?P<day>([0-9]{1,2}))_(?P<year>([0-9]{1,4}))_(?P<page>[0-9]{1,2}).html"
            )
            files = helpers.get_files(directory)
            for filename in list(f for f in files if re.match(file_pattern, f)):
                match = re.match(file_pattern, filename)
                timestamp = helpers.build_filename_timestamp(match)
                with open(filename, 'rb') as f:
                    soup = BeautifulSoup(f, 'html.parser')
                    for listing in self.extract_listings(soup, timestamp):
                        self._store(listing)

        if scrape_results:
            for html_obj in scrape_results:
                soup = BeautifulSoup(hmtl_obj, 'html.parser')
                timestamp = datetime.datetime.now().strftime("%Y:%m:%d %H:%M:%S")
                for listing in self.extract_listings(soup, timestamp):
                    self._store(listing)

class DataStoreNotSpecifiedError(Exception):
    """
    """
    pass
