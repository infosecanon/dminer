"""
The alphabay sink module provides the ability to scrape raw data (HTML) from
the onion site that is hosting it, then (if specified) save it to disk, send it
through an ingestion point, and save it in a datastore.
"""
import os
from dminer.ingestion.alphabay import AlphabayParser
from dminer.stores.interfaces import ElasticsearchInterface, STDOutInterface
from alphabay import *


def prepare_cli(parser):
    """
    Prepares the CLI subgroup parser by adding arguments specific to the 
    alphabay sink. It also sets the entry point for the CLI to use when
    specifying this subgroup.
    """
    # Sink related arguments
    parser.add_argument(
        "-u", "--alphabay-username",
        default=os.environ.get("DMINER_SINK_ALPHABAY_USERNAME", None),
        help="""
        Specifies the username to use for the login form on Alpha Bay. It is
        also able to be specified as an environment variable: DMINER_SINK_ALPHABAY_USERNAME.
        This is required for this sink module.
        """
    )
    parser.add_argument(
        "-p", "--alphabay-password",
        default=os.environ.get("DMINER_SINK_ALPHABAY_PASSWORD", None),
        help="""
        Specifies the password to use for the login form on Alpha Bay. It is
        also able to be specified as an environment variable: DMINER_SINK_ALPHABAY_PASSWORD.
        This is required for this sink module.
        """
    )
    parser.add_argument(
        "-k", "--dbc-access-key",
        default=os.environ.get("DMINER_DBC_ACCESS_KEY", None),
        help="""
        Specifies the access key to use for deathbycaptcha. It is also able to 
        be specified as an environment variable: DMINER_DBC_ACCESS_KEY.
        This is required for this sink module.
        """
    )
    parser.add_argument(
        "-s", "--dbc-secret-key",
        default=os.environ.get("DMINER_DBC_SECRET_KEY", None),
        help="""
        Specifies the secret key to use for deathbycaptcha. It is also able to 
        be specified as an environment variable: DMINER_DBC_SECRET_KEY.
        This is required for this sink module.
        """
    )
    parser.add_argument(
        "--onion-url",
        default=os.environ.get("DMINER_SINK_ALPHABAY_ONION_URL", "http://pwoah7foa6au2pul.onion"),
        help="""
        Specifies the onion URL to use for this marketplace. It is also able to
        be specified as an environment variable: DMINER_SINK_ALPHABAY_ONION_URL.
        This is required for this sink module. The default is: %(default)s.
        """
    )
    parser.add_argument(
        "--url-file",
        default=None,
        help="""
        Specifies the file to use for defining URLs to be consumed by the
        scraper. If specified, only the URL's in the file will be scraped, and
        the sink will exit after all URL's from the file have been exhausted.
        """
    )
    parser.add_argument(
        "--save-to-directory",
        default=None,
        help="""
        If specified, the sink will attempt to save all scraped HTML files to 
        the specified directory.
        """
    )
    
    # Flag to also perform ingestion
    parser.add_argument(
        "--ingest",
        action="store_true",
        help="""
        If specified, the sink will pass all scraped HTML files to the Alpha 
        Bay ingestion point, with the ingestion point being configured to use
        the specified datstore interface.
        """
    )
    
    # Datastore related arguments
    parser.add_argument(
        "--datastore",
        default="stdout",
        choices=["stdout", "elasticsearch"],
        help="""
        Specify the datastore to use during ingestion. The default datastore is
        %(default)s.
        """
    )
    parser.add_argument(
        "--datastore-host",
        default="localhost",
        help="""
        Specify the datastore remote host. The default host is %(default)s.
        """
    )
    parser.add_argument(
        "--datastore-port",
        default=9200,
        help="""
        Specify the datastore remote port. The default port is %(default)s.
        """
    )
    parser.set_defaults(func=entry)

def entry(arguments):
    """
    The entry point for the alphabay sink CLI interface. This defines the logic 
    around the usage of command line arguments and the alphabay sink in order
    to perform scraping, ingestion, and storage related functions.
    """
    if not arguments.alphabay_username:
        logger.error("This sink requires a username to be specified through CLI or enviornment variable.")
        raise SystemExit()
    if not arguments.alphabay_password:
        logger.error("This sink requires a password to be specified through CLI or environment variable.")
        raise SystemExit()
    
    if not arguments.dbc_access_key:
        logger.error("This sink requires a deathbycaptcha access key to be specified through CLI or environment variable.")
        raise SystemExit()
    if not arguments.dbc_secret_key:
        logger.error("This sink requires a deathbycaptcha secret key to be specified through CLI or environment variable.")
        raise SystemExit()
    
    sink = AlphabaySink(
        arguments.alphabay_username, arguments.alphabay_password,
        arguments.dbc_access_key, arguments.dbc_secret_key,
        url_file=arguments.url_file, save_to_directory=arguments.save_to_directory,
        onion_url=arguments.onion_url
    )
    
    if arguments.ingest:
        if arguments.datastore == "stdout":
            store = STDOutInterface()
            
            parser = AlphabayParser(datastore=store)
            parser.parse(scrape_results=sink.scrape())

        elif arguments.datastore == "elasticsearch":
            store = ElasticsearchInterface(
                host=arguments.datastore_host,
                port=arguments.datastore_port
            )
            
            parser = AlphabayParser(datastore=store)
            parser.parse(scrape_results=sink.scrape())
    else:
        sink.scrape()
