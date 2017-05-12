"""
TODO: DOC
"""
import logging
from elasticsearch import Elasticsearch
from dminer.stores.configuration.alphabay.elasticsearch import AlphabayElasticsearchConfiguration
from dminer.stores.configuration.dreammarket.elasticsearch import DreammarketElasticsearchConfiguration

class MasterElasticsearchConfiguration(object):
    """
    TODO: DOC
    """
    def __init__(self, host="localhost", port=9200):
        self.config_drivers = [
            AlphabayElasticsearchConfiguration(host=host, port=port),
            DreammarketElasticsearchConfiguration(host=host, port=port)
        ]
        # Set current logger
        self.logger = logging.getLogger(__name__)
        
        # Patch driver loggers so that they are in this configuration's
        # namespace.
        for driver in self.config_drivers:
            driver.logger = self.logger
    
    def create(self):
        """
        TODO: DOC
        """
        for driver in self.config_drivers:
            driver.create()

    def destroy(self):
        """
        TODO: DOC
        """
        for driver in self.config_drivers:
            driver.destroy()
    
    def info(self):
        """
        TODO: DOC
        """
        for driver in self.config_drivers:
            driver.info()
