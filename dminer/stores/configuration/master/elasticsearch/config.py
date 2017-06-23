"""
This module contains the `dminer.stores.configuration.master.elasticsearch.MasterElasticsearchConfiguration`
class, which provides interactions with all Elasticsearch configuration modules
on a top level, instead of performing each module action individually.
"""
import logging
from elasticsearch import Elasticsearch
from dminer.stores.configuration.alphabay.elasticsearch import AlphabayElasticsearchConfiguration
from dminer.stores.configuration.dreammarket.elasticsearch import DreammarketElasticsearchConfiguration

class MasterElasticsearchConfiguration(object):
    """
    This class contains methods to interact with supported configuration modules.
    This interaction involves interfacing with the creation, deletion, and
    info grabbing actions of these configuration modules.
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
        Calls all of the create methods for each of the congiguration modules.
        """
        for driver in self.config_drivers:
            driver.create()

    def destroy(self):
        """
        Calls all of the destroy methods for each of the configuration modules.
        """
        for driver in self.config_drivers:
            driver.destroy()
    
    def info(self):
        """
        Calls all of the info methods for each of the configuration modules.
        """
        for driver in self.config_drivers:
            driver.info()
