"""
The elasticsearch configuration module provides the ability to retreive
information regarding what is currently loaded in a given elasticsearch 
instance, create an index template for use with the alphabay ingestion module,
as well as destroy an index's template and data.
"""
from config import *
import logging

logger = logging.getLogger(__name__)

def prepare_cli(parser):
    """
    Prepares the CLI sugroup parser by adding arguments specific to the
    alphabay elasticsearch configuration module. It also sets the entry point
    for the CLI to use when specifying this subgroup.
    """
    # Elasticsearch configuration module related arguments
    parser.add_argument(
        "-v", "--verbosity",
        default="info",
        choices=["debug", "info", "warn", "error"],
        help="""
        Controls the verbosity of the configuration module. Default is 
        %(default)s.
        """
    )
    
    # Datastore related arguments
    parser.add_argument(
        "-r","--remote-host",
        default="localhost",
        help="""
        Specify the Elasticsearch remote host. The default host is %(default)s.
        """
    )
    parser.add_argument(
        "-p", "--remote-port",
        type=int,
        default=9200,
        help="""
        Specify the Elasticsearch remote port. The default port is %(default)s.
        """
    )
    parser.add_argument(
        "-a", "--action",
        default="info",
        choices=["info", "create", "destroy"],
        help="""
        Specify the aciton to perform on the Elasticsearch instance. Default
        is %(default)s.
        """
    )
    parser.set_defaults(func=entry)

def entry(arguments):
    """
    The entry point for the elasticsearch configuration module. This defines
    the logic around the usage of command line arguments with the configuration
    module.
    """
    logger.setLevel(arguments.verbosity.upper())
    
    config = AlphabayElasticsearchConfiguration(
        host=arguments.remote_host,
        port=arguments.remote_port
    )
    
    if arguments.action == "info":
        config.info()
    elif arguments.action == "create":
        config.create()
    elif arguments.action == "destroy":
        config.destroy()
