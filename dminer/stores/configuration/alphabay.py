from elasticsearch import Elasticsearch
import logging


class AlphabayConfiguration(object):
    """
    Controls the configuration of backend datastores supported by the Alphabay
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
        Creates the elasticsearch index configuration for Alphabay. It does
        this through the creation of the index template:

            dminer-alphabay-template

        This configuration cascades for all indexes matching:

            dminer-alphabay-*

        The explicitly typed fields are as follows:

            listing_price:
              BTC -> double
              USD -> double
            listing_item_number -> integer
            listing_views -> integer
            listing_date -> date (yyyy-MM-dd)
            timestamp -> date (yyyy:MM:dd HH:mm:ss:SSS)

        This configuration also controls the number of replica shards for each
        index matching the template index matching expression (dminer-alphabay-*).
        """

        settings = {
            "template": "dminer-alphabay-*",
            "settings": {
                "number_of_shards" :   1,
                "number_of_replicas" : 0
            },
            "mappings": {
                "alphabay_listing":{
                    "properties": {
                        "listing_price": {
                            "type": "nested",
                            "properties": {
                                "BTC": {
                                    "type": "double"
                                },
                                "USD": {
                                    "type": "double"
                                }
                            }
                        },
                        "listing_item_number": {
                            "type": "integer"
                        },
                        "listing_views": {
                            "type": "integer"
                        },
                        "listing_date": {
                            "type": "date",
                            "format": "yyyy-MM-dd"
                        },
                        "timestamp": {
                            "type": "date",
                            "format": "yyyy:MM:dd HH:mm:ss:SSS"
                        }
                    }
                }
            }
        }

        es = Elasticsearch([":".join([str(self.datastore_host), str(self.datastore_port)])])
        self.logger.info("Creating index template for dminer-alphabay-* with settings: %s" % str(settings))
        es.indices.put_template("dminer-alphabay-template", body=settings)
        self.logger.info("Successfully creaetd index template for dminer-alphabay-*.")

    def _destroy_elasticsearch(self):
        """
        Deletes all elasticsearch history for Alphabay. It will delete all
        indexes matching:

            dminer-alphabay-*

        It will also delete the template for indexes. This template is named:

            dminer-alphabay-template
        """

        es = Elasticsearch([":".join([str(self.datastore_host), str(self.datastore_port)])])
        self.logger.info("Deleting index: dminer-alphabay-*")
        es.indices.delete("dminer-alphabay-*")
        self.logger.info("Deleting index template: dminer-dreammarket-template")
        es.indices.delete_template("dminer-alphabay-template")
