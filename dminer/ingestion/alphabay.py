from bs4 import BeautifulSoup
import json, re, os, logging, helpers

class AlphabayParser(object):
    """
    """

    def __init__(self, datastore=None):
        """
        """

        self.datastore = datastore
        self.logger = logging.getLogger(__name__)

    def _store(self, item):
        """
        """

        if isinstance(self.datastore, type(None)):
            raise DataStoreNotSpecifiedError("A datastore must be present in order to store a parsed result.")
        self.datastore.create(
            document=item,
            type="alphabay_listing",
            parser="alphabay",
            index_date_field="listing_date"
        )

    def extract_listings(self, bs_obj, timestamp):
        """
        """

        listings = bs_obj.find_all("div", class_="listing")
        for listing_element in listings:
            image_div = listing_element.find("div", class_="tcl")
            pricing_div = listing_element.find("div", class_="tclr")
            primary_div = listing_element.find("div", style="margin-left:90px;margin-right:120px;")

            item = {}
            item["market_name"] = "Alphabay"
            item["listing_name"] = primary_div.find("a", class_="bstd").text

            # Parse pricing
            price_string = pricing_div.find("span", class_="std").text.strip()

            usd_price = price_string.split("\n")[0].split(" ")
            usd_price = usd_price[len(usd_price)-1].replace(",", "")

            btc_price = price_string.split("\n")[1].split(" ")
            btc_price = btc_price[0].lstrip("(")

            item["listing_price"] = {
                "USD": usd_price,
                "BTC": btc_price
            }
            # Split the element value by "-" so that we can grab item number and category.
            # Text being parsed looks like: "Item # 30361 - Botnets & Malware / Botnets & Malware"
            item_number, item_category = tuple(value.strip() for value in primary_div.find("span", class_="std", style="line-height:12px;").text.split("-"))
            item["listing_item_number"] = int(item_number.split("#")[1].strip())
            item["listing_category"] = item_category

            # Grab who is listing this item
            vendor_id = primary_div.find("span", class_="normal")
            if not vendor_id:
                vendor_id = primary_div.find("span", class_="red")
                if not vendor_id:
                    raise Exception("Error with CSS")
                vendor_id = vendor_id.text.split("-")[2].split(" ")
                vendor_name = vendor_id[0].strip()
                vendor_id = vendor_id[len(vendor_id) - 1].lstrip("(").rstrip(")")
            else:
                vendor_name = primary_div.find("span", class_="normal").find("a", class_="std").text
                vendor_id = vendor_id.text
                vendor_id = vendor_id.strip().split("(")[1].rstrip(")")
            item["listing_vendor"] = {
                "name": vendor_name,
                "id": int(vendor_id)
            }

            # Grab views, bids, and quantities
            meta_info = list(parent for parent in primary_div.find_all("span", class_="std") if "Bid" in parent.text)[0].text
            view_bid_info, quantity_info = tuple(meta_info.split("Quantity left: "))
            item["listing_views"] = int(view_bid_info.split("/")[0].split(" ")[1])
            item["listing_bids"] = view_bid_info.split("/")[1].strip().split(": ")[1]
            item["item_quantity"] = quantity_info

            # Grab the listing date from the listing image
            image_date = image_div.find("a", class_="notext").find("img", class_="listing")['src']
            image_date = "-".join(image_date.split("images/uploads/")[1].split("/")[:3])
            item["listing_date"] = image_date
            item["timestamp"] = timestamp
            yield item

    def parse(self, directory=None, scrape_results=None, **kwargs):
        """
        The fetched files can be controlled
        Through the use of the environment variable:

            DMINER_ALPHABAY_PARSER_FILENAME_FORMAT

        For example, on a linux host you can perform:

            export DMINER_ALPHABAY_PARSER_FILENAME_FORMAT=".*(?P<market_name>alphabay)_(?P<market_category>.*)_(?P<month>\d\d)_(?P<day>\d\d)_(?P<year>\d\d).html"
        """

        if directory:
            file_pattern = os.environ.get(
                "DMINER_ALPHABAY_PARSER_FILENAME_FORMAT",
                ".*(?P<market_name>alphabay)_(?P<market_category>.*)_(?P<month>\d\d)_(?P<day>\d\d)_(?P<year>\d\d).html"
            )
            files = helpers.get_files(directory)
            for filename in list(f for f in files if re.match(pattern, f)):
                match = re.match(pattern, filename)
                timestamp = build_filename_timestamp(match)
                with open(filename, 'rb') as f:
                    soup = BeautifulSoup(f, 'html.parser')
                    for listing in self.extract_listings(soup, timestamp):
                        self._store(listing)

        if scrape_results:
            for html_obj in scrape_results:
                soup = BeautifulSoup(html_obj, 'html.parser')
                timestamp = datetime.datetime.now().strftime("yyyy:MM:dd HH:mm:ss:SSS")
                for listing in self.extract_listings(soup, timestamp):
                    self._store(listing)

class DataStoreNotSpecifiedError(Exception):
    """
    """
    pass
