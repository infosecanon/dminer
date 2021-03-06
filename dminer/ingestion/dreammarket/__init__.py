"""
The Dream Market ingestion module provides the ability to ingest HTML documents
that have been scraped from the Dream Market darknet marketplace.
"""
import logging
from dminer.stores.interfaces import ElasticsearchInterface
from dreammarket import *

logger = logging.getLogger(__name__)

def prepare_cli(parser):
    """
    Prepares the CLI subgroup parser by adding arguments specific to the
    Dream Market ingestion point. It also sets the entry point for the CLI to
    use when specifying this sub group.
    """
    # Ingestion related arguments
    parser.add_argument(
        "ingestion_directory",
        default=None,
        help="""
        The directory where scrape files are located. The directory should be
        flat, as subdirectories will not be traversed for other files.
        """
    )
    parser.add_argument(
        "-v", "--verbosity",
        default="info",
        choices=["debug", "info", "warn", "error"],
        help="""
        Controls the verbosity of the ingestion point. Default is %(default)s.
        """
    )
    
    # Datastore related arguments
    parser.add_argument(
        "-d", "--datastore",
        default="none",
        choices=["none", "elasticsearch"],
        help="""
        Specify the datastore to store parsed entries in. Default is %(default)s.
        """
    )
    parser.add_argument(
        "-r", "--datastore-host",
        default="localhost",
        help="""
        Specify the remote host of the datastore. Default is %(default)s.
        """
    )
    parser.add_argument(
        "-p", "--datastore-port",
        type=int,
        default=9200,
        help="""
        Specify the remote port of the datastore. Default is %(default)s.
        """
    )
    parser.set_defaults(func=entry)

def entry(arguments):
    """
    The entry point for the Dream Market ingestion point. Performs execution 
    logic based on the defined arguments, and their corresponding values.
    """
    # Set log level to user specified level
    logger.setLevel(arguments.verbosity.upper())
    # Default to none. Should trigger stdout ingestion (good for testing)
    store_interface = None
    if arguments.datastore == "none":
        store_interface = None
    elif arguments.datastore == "elasticsearch":
        store_interface = ElasticsearchInterface(
            host=arguments.datastore_host,
            port=arguments.datastore_port
        )
    
    parser = DreammarketParser(datastore=store_interface)
    parser.parse(directory=arguments.ingestion_directory)
