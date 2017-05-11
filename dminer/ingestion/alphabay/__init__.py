"""
The alphabay ingestion module provides the ability to ingest HTML documents
that have been scraped from the alphabay darknet marketplace.
"""
import logging
from dminer.stores.interfaces import ElasticsearchInterface, STDOutInterface
from alphabay import *

logger = logging.getLogger(__name__)

def prepare_cli(parser):
    """
    Prepares the CLI subgroup parser by adding arguments specific to the
    alphabay ingestion point. It also sets the entry point for the CLI to use 
    when specifying this subgroup.
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
        default="stdout",
        choices=["stdout", "elasticsearch"],
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
    The entry point for the alphabay ingestion point. Performs execution logic
    based on the defined arguments, and their corresponding values.
    """
    # Set log level to user specified level
    logger.setLevel(arguments.verbosity.upper())

    if arguments.datastore == "stdout":
        store = STDOutInterface()
    elif arguments.datastore == "elasticsearch":
        store = ElasticsearchInterface(
            host=arguments.datastore_host,
            port=arguments.datastore_port
        )
    
    parser = AlphabayParser(datastore=store)
    parser.parse(directory=arguments.ingestion_directory)
