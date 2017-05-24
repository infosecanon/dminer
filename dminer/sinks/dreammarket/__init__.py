"""
The dreammarket sink module provides the ability to scrape raw data (HTML) from
the onion site that is hosting it, then (if specified) save it to disk, send it
through an ingestionion point, and save it in a datastore.
"""
import os
from dminer.ingestion.dreammarket import DreammarketParser
from dminer.stores.interfaces import ElasticsearchInterface, STDOutInterface
from dreammarket import *


def prepare_cli(parser):
    """
    Prepares the CLI subgroup parser by adding arguments specific to the
    dreammarket sink. It also sets the entry point for the CLI to use when
    specifying this subgroup.
    """
    # Sink related arguments
    parser.add_argument(
        "-u", "--dreammarket-username",
        default=os.environ.get("DMINER_SINK_DREAMMARKET_USERNAME", None),
        help="""
        Specifies the username to use for the login form on Dream Market. It is
        also able to be specified as an environment variable: DMINER_SINK_DREAMMARKET_USERNAME.
        This is required for this sink module.
        """
    )
    parser.add_argument(
        "-p", "--dreammarket-password",
        default=os.environ.get("DMINER_SINK_DREAMMARKET_PASSWORD", None),
        help="""
        Specifies the password to use for the login form on Dream Market. It is
        also able to be specified as an environment variable: DMINER_SINK_DREAMMARKET_PASSWORD.
        This is a required for this sink module.
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
        default=os.environ.get("DMINER_SINK_DREAMMARKET_ONION_URL", "onion_goes_here"),
        help="""
        Specifies the onion URL to use for this marketplace. It is also able to
        be specified as an environment variable: DMINER_SINK_DREAMMARKET_ONION_URL.
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
        If specified, the sink will pass all scraped HTML files to the DreamMarket 
        ingestion point, with the ingestion point being configured to use the 
        specified datstore interface.
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
    The entry point for the dreammarket sink CLI interface. This defines the
    logic around the usage of command line arguments and the dreammarket sink in
    order to perform scraping, ingestion, and storage related functions.
    """
    if not arguments.dreammarket_username:
        logger.error("This sink requires a username to be specified through CLI or enviornment variable.")
        raise SystemExit()
    if not arguments.dreammarket_password:
        logger.error("This sink requires a password to be specified through CLI or environment variable.")
        raise SystemExit()
    
    if not arguments.dbc_access_key:
        logger.error("This sink requires a deathbycaptcha access key to be specified through CLI or environment variable.")
        raise SystemExit()
    if not arguments.dbc_secret_key:
        logger.error("This sink requires a deathbycaptcha secret key to be specified through CLI or environment variable.")
        raise SystemExit()
    
    sink = DreammarketSink(
        arguments.dreammarket_username, arguments.dreammarket_password,
        arguments.dbc_access_key, arguments.dbc_secret_key,
        url_file=arguments.url_file, save_to_directory=arguments.save_to_directory,
        onion_url=arguments.onion_url
    )
    
    if arguments.ingest:
        if arguments.datastore == "stdout":
            store = STDOutInterface()
            
            parser = DreammarketParser(datastore=store)
            parser.parse(scrape_results=sink.scrape())

        elif arguments.datastore == "elasticsearch":
            store = ElasticsearchInterface(
                host=arguments.datastore_host,
                port=arguments.datastore_port
            )
            
            parser = DreammarketParser(datastore=store)
            parser.parse(scrape_results=sink.scrape())
    else:
        sink.scrape()
