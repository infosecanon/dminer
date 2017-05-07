"""
"""
import os, sys
from alphabay import *


def prepare_cli(parser):
    """
    """
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
        "--url-file",
        type=str,
        help=""
    )
    parser.set_defaults(func=entry)

def entry(arguments):
    """
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
    
    sink = AlphabaySink()
