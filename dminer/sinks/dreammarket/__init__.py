"""
The dreammarket sink module provides the ability to scrape raw data (HTML) from
the onion site that is hosting it, then (if specified) save it to disk, send it
through an ingestionion point, and save it in a datastore.
"""
import os
import logging
from dminer.ingestion.dreammarket import DreammarketParser
from dminer.stores.interfaces import ElasticsearchInterface, STDOutInterface
from dreammarket import *

logger = logging.getLogger(__name__)


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
        default=os.environ.get(
            "DMINER_SINK_DREAMMARKET_ONION_URL", "http://lchudifyeqm4ldjj.onion"
        ),
        help="""
        Specifies the onion URL to use for this marketplace. It is also able to
        be specified as an environment variable: DMINER_SINK_DREAMMARKET_ONION_URL.
        This is required for this sink module. The default is: %(default)s.
        """
    )

    url_category_exclusive_group = parser.add_mutually_exclusive_group()
    url_category_exclusive_group.add_argument(
        "--url-file",
        default=None,
        help="""
        Specifies the file to use for defining URLs to be consumed by the
        scraper. If specified, only the URL's in the file will be scraped, and
        the sink will exit after all URL's from the file have been exhausted.
        """
    )
    url_category_exclusive_group.add_argument(
        "--category",
        default="security & hosting",
        help="""
        Specifies the category to pull URLS from for consumption by the
        scraper. If specified, URL's will be pulled dynamically, and the
        category specified will be used to look up where to pull the URLs.
        The default is '%(default)s'.
        """
    )

    parser.add_argument(
        "--daemonize",
        action="store_true",
        help="""
        If specified, the scraper will be put into a daemon mode, which will
        repeatedly run, refreshing URLS to scrape based on the CLI options
        provided (either --category or --url-file).
        """
    )
    parser.add_argument(
        "--request-interval",
        default=15, type=int,
        help="""
        The request interval is the maximum amount of time to wait in between
        requests for each page being scraped. The actual amount of time in
        between requests is random, ranging between 0 and the interval
        specified. The default is %(default)i seconds.
        """
    )
    parser.add_argument(
        "--request-retries",
        default=5, type=int,
        help="""
        The request retry metric is used to determine how many attempts should
        be made to scrape a particular page before skipping the URL. The
        default is %(default)i seconds.
        """
    )
    parser.add_argument(
        "--request-timeout",
        default=5, type=int,
        help="""
        The request timeout metric is used to determine how long a request
        should persist without a response. The default is %(default)i seconds.
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
    parser.add_argument(
        "-v", "--verbosity",
        default="info",
        choices=["debug", "info", "warn", "error"],
        help="""
        Controls the verbosity of the ingestion point. Default is %(default)s.
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
    The entry point for the dreammarket sink CLI interface. This defines the
    logic around the usage of command line arguments and the dreammarket sink in
    order to perform scraping, ingestion, and storage related functions.
    """
    logger.setLevel(arguments.verbosity.upper())
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
        url_file=arguments.url_file,
        save_to_directory=arguments.save_to_directory,
        onion_url=arguments.onion_url,
        request_interval=arguments.request_interval,
        request_retries=arguments.request_retries,
        request_timeout=arguments.request_timeout,
        category=arguments.category
    )
    sink.logger = logger

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
            parser.parse(
                scrape_results=sink.scrape(
                    daemon=arguments.daemonize
                )
            )
    else:
        list(sink.scrape())
