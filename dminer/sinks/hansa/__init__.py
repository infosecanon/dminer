"""
TODO: DOC
"""
import os
import logging


from dminer.ingestion.hansa import HansaParser
from dminer.stores.interfaces import ElasticsearchInterface, STDOutInterface
from hansa import *

logger = logging.getLogger(__name__)


def prepare_cli(parser):
    """
    TODO: DOC
    """
    parser.add_argument(
        "--onion-url",
        default=os.environ.get(
            "DMINER_SINK_HANSA_ONION_URL", "http://hansamkt2rr6nfg3.onion"
        ),
        help="""
        Specifies the onion URL to use for this marketplace. It is also able to
        be specified as an environment variable: DMINER_SINK_HANSA_ONION_URL.
        This is required for this sink module. The default is: %(default)s.
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
    TODO: DOC
    """
    logger.setLevel(arguments.verbosity.upper())

    sink = HansaSink(
        arguments.dbc_access_key, arguments.dbc_secret_key,
        onion_url=arguments.onion_url,
        url_file=arguments.url_file,
        save_to_directory=arguments.save_to_directory,
        request_interval=arguments.request_interval,
        request_retries=arguments.request_retries,
        request_timeout=arguments.request_timeout,
        category=arguments.category
    )
    sink.logger = logger

    if arguments.ingest:
        if arguments.datastore == "stdout":
            store = STDOutInterface()

            parser = HansaParser(datastore=store)
            parser.parse(scrape_results=sink.scrape())
        elif arguments.datastore == "elasticsearch":
            store = ElasticsearchInterface(
                host=arguments.datastore_host,
                port=arguments.datastore_port
            )

            parser = HansaParser(datastore=store)
            parser.parse(
                scrape_results=sink.scrape(
                    daemon=arguments.daemonize
                )
            )
    else:
        list(sink.scrape(daemon=sink))
