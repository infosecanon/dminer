"""
TODO: DOC
"""
from config import *


def prepare_cli(parser):
    """
    TODO: DOC
    """
    parser.add_argument(
        "-d", "--datastore",
        default="elasticsearch",
        choices=["elasticsearch"]
    )
    parser.add_argument(
        "-a", "--action",
        default="info",
        choices=["info", "create", "destroy"]
    )
    parser.add_argument(
        "-v", "--verbosity",
        default="info",
        choices=["debug", "info", "warn"]
    )
    parser.set_defaults(func=entry)

def entry(arguments):
    """
    """
    pass
