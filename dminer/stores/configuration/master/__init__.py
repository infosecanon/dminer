"""
"""
from master import *


def prepare_cli(parser):
    """
    """
    parser.add_argument(
        "-d", "--datastore",
        default="elasticsearch",
        const="elasticsearch",
        nargs="?",
        choices=["elasticsearch"]
    )
    parser.add_argument(
        "-a", "--action",
        default="info",
        const="info",
        nargs="?",
        choices=["info", "create", "destroy"]
    )
    parser.add_argument(
        "-v", "--verbosity",
        default="info",
        const="info",
        nargs="?",
        choices=["debug", "info", "warn"]
    )
    parser.set_defaults(func=entry)

def entry(arguments):
    """
    """
    pass
