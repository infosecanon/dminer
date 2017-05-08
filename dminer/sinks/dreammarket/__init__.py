"""
TODO: DOC
"""
import os, sys
from dreammarket import *


def prepare_cli(parser):
    """
    TODO: DOC
    """
    parser.add_argument(
        "-u", "--dreammarket-username",
        default=os.environ.get("DMINER_SINK_DREAMMARKET_USERNAME", None),
        help=""
    )
    parser.add_argument(
        "-p", "--dreammarket-password",
        default=os.environ.get("DMINER_SINK_DREAMMARKET_PASSWORD", None),
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
        default=os.environ.get("DMINER_SINK_DREAMMARKET_ONION_URL", "onion_goes_here"),
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
    parser.set_defaults(func=entry)

def entry(arguments):
    """
    TODO: DOC
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
    
    sink.scrape()
