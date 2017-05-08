"""
TODO: DOC
"""
import os
from dminer.ingestion.alphabay import AlphabayParser
from dminer.stores.interfaces import ElasticsearchInterface
from alphabay import *


def prepare_cli(parser):
    """
    TODO: DOC
    """
    # Sink related arguments
    parser.add_argument(
        "-u", "--alphabay-username",
        default=os.environ.get("DMINER_SINK_ALPHABAY_USERNAME", None),
        help=""
    )
    parser.add_argument(
        "-p", "--alphabay-password",
        default=os.environ.get("DMINER_SINK_ALPHABAY_PASSWORD", None),
        help=""
    )
    parser.add_argument(
        "-k", "--dbc-access-key",
        default=os.environ.get("DMINER_DBC_ACCESS_KEY", None),
        help=""
    )
    parser.add_argument(
        "-s", "--dbc-secret-key",
        default=os.environ.get("DMINER_DBC_SECRET_KEY", None),
        help=""
    )
    parser.add_argument(
        "--onion-url",
        default=os.environ.get("DMINER_SINK_DREAMMARKET_ONION_URL", "http://pwoah7foa6au2pul.onion"),
        help=""
    )
    parser.add_argument(
        "--url-file",
        default=None,
        help=""
    )
    parser.add_argument(
        "--save-to-directory",
        default=None,
        help=""
    )
    
    # Flag to also perform ingestion
    parser.add_argument(
        "--ingest",
        action="store_true",
        help=""
    )
    
    # Datastore related arguments
    parser.add_argument(
        "--datastore",
        default="elasticsearch",
        const="elasticsearch",
        choices=["elasticsearch", "none"],
        help=""
    )
    parser.add_argument(
        "--datastore-host",
        default="localhost",
        help=""
    )
    parser.add_argument(
        "--datastore-port",
        default=9200,
        help=""
    )
    parser.set_defaults(func=entry)

def entry(arguments):
    """
    TODO: DOC
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
        if arguments.datastore == "none":
            parser = AlphabayParser()
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
