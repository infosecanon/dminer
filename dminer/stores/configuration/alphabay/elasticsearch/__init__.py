"""
TODO: DOC
"""
from config import *
import logging

logger = logging.getLogger(__name__)

def prepare_cli(parser):
    """
    TODO: DOC
    """
    parser.add_argument(
        "-r","--remote-host",
        default="localhost",
        help=""
    )
    parser.add_argument(
        "-p", "--remote-port",
        type=int,
        default=9200,
        help=""
    )
    parser.add_argument(
        "-a", "--action",
        default="info",
        const="info",
        nargs="?",
        choices=["info", "create", "destroy"],
        help=""
    )
    parser.add_argument(
        "-v", "--verbosity",
        default="info",
        const="info",
        nargs="?",
        choices=["debug", "info", "warn", "error"],
        help=""
    )
    parser.set_defaults(func=entry)

def entry(arguments):
    """
    TODO: DOC
    """
    logger.setLevel(arguments.verbosity.upper())
    
    config = AlphabayElasticsearchConfiguration(
        arguments.remote_host,
        arguments.remote_port
    )
    
    if arguments.action == "info":
        config.info()
    elif arguments.action == "create":
        config.create()
    elif arguments.action == "destroy":
        config.destroy()
