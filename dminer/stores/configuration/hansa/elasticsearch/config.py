import logging
from pprint import pformat
from elasticsearch import Elasticsearch


class HansaElasticsearchConfiguration(object):
    """
    Controls the configuration of elasticsearch supported by the Hansa
    ingestion point. Currently, the spported actions are:

          create
          destroy
    """

    def __init__(self, host="localhost", port=9200):
        """
        Bootstraps logging & elasticsearch configuration variables.
        """

        self.host = host
        self.port = port
        self.logger = logging.getLogger(__name__)

    def create(self):
        """
        Creates the elasticsearch index configuration for Hansa. It does
        this through the creation of the index template:

            dminer-hansa-template

        This configuration cascades for all indexes matching:

            dminer-hansa-*

        The explicitly typed fields are as follows:

            listing_price_btc -> double
            listing_price_usd -> double
            listing_item_number -> integer
            listing_views -> integer
            timestamp -> date (yyyy:MM:dd HH:mm:ss)

        This configuration also controls the number of replica shards for each
        index matching the template index matching expression (dminer-hansa-*).
        """

        settings = {
            "template": "dminer-hansa-*",
            "settings": {
                "number_of_shards" :   1,
                "number_of_replicas" : 0
            },
            "mappings": {
                "hansa_listing":{
                    "properties": {
                        "listing_price_btc": {
                            "type": "double"
                        },
                        "listing_price_usd": {
                            "type": "double"
                        },
                        "listing_item_number": {
                            "type": "integer"
                        },
                        "listing_views": {
                            "type": "integer"
                        },
                        "timestamp": {
                            "type": "date",
                            "format": "yyyy:MM:dd HH:mm:ss"
                        }
                    }
                }
            }
        }

        es = Elasticsearch(
            [
                ":".join([self.host, str(self.port)])
            ]
        )
        self.logger.info("Creating index template for dminer-hansa-* with settings: \n%s" % pformat(settings))
        es.indices.put_template("dminer-hansa-template", body=settings)
        self.logger.info("Successfully creaetd index template for dminer-hansa-*.")

    def destroy(self):
        """
        Deletes all elasticsearch history for Hansa. It will delete all
        indexes matching:

            dminer-hansa-*

        It will also delete the template for indexes. This template is named:

            dminer-hansa-template
        """

        es = Elasticsearch([":".join([str(self.host), str(self.port)])])
        self.logger.info("Deleting index: dminer-hansa-*")
        es.indices.delete("dminer-hansa-*")
        self.logger.info("Deleting index template: dminer-dreammarket-template")
        es.indices.delete_template("dminer-hansa-template")

    def info(self):
        """
        This method provides information regarding the hansa elasticsearch
        configuration currently in the specified database.
        """
        pass
