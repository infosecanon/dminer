from elasticsearch import Elasticsearch
import logging


class DreammarketConfiguration(object):
    """
    Controls the configuration of backend datastores supported by the DreamMarket
    ingestion point. Currently, the spported actions are:

        Elasticsearch:
          create
          destroy
    """

    def __init__(self,
                 datastore_host="localhost",
                 datastore_port=9200):
        """
        Bootstraps logging & datastore configuration variables.

        The `datastore_host` and `datastore_port` are used inside of the
        individual database configuration functions for configuration.
        """
        self.datastore_host = datastore_host
        self.datastore_port = datastore_port
        self.logger = logging.getLogger(__name__)

    def _create_elasticsearch(self):
        """
        Creates the elasticsearch index configuration for DreamMarket. It does
        this through the creation of the index template:

            dminer-dreammarket-template

        This configuration cascades for all indexes matching:

            dminer-dreammarket-*

        The explicitly typed fields are as follows:

            listing_price_btc -> double
            vendor_transactions -> integer
            vendor_rating -> double
            timestamp -> date (yyyy:MM:dd HH:mm:ss:SSS)
        """

        settings = {
            "template": "dminer-dreammarket-*",
            "settings": {
                "number_of_shards" :   1,
                "number_of_replicas" : 0
            },
            "mappings": {
                "dreammarket_listing":{
                    "properties": {
                        "listing_price_btc": {
                            "type": "double"
                        },
                        "vendor_transactions": {
                            "type": "integer"
                        },
                        "vendor_rating": {
                            "type": "double"
                        },
                        "timestamp": {
                            "type": "date",
                            "format": "yyyy:MM:dd HH:mm:ss"
                        }
                    }
                }
            }
        }

        es = Elasticsearch([":".join([str(self.datastore_host), str(self.datastore_port)])])
        self.logger.info("Creating index template for dminer-dreammarket-* with settings: %s" % str(settings))
        es.indices.put_template("dminer-dreammarket-template", body=settings)
        self.logger.info("Successfully creaetd index template for dminer-dreammarket-*.")

    def _destroy_elasticsearch(self):
        """
        Deletes all elasticsearch history for DreamMarket. It will delete all
        indexes matching:

            dminer-dreammarket-*

        It will also delete the template for indexes. This template is named:

            dminer-dreammarket-template
        """

        es = Elasticsearch([":".join([str(self.datastore_host), str(self.datastore_port)])])
        self.logger.info("Deleting index: dminer-dreammarket-*")
        es.indices.delete("dminer-dreammarket-*")
        self.logger.info("Deleting index template: dminer-dreammarket-template")
        es.indices.delete_template("dminer-dreammarket-template")
