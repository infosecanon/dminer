"""
The base ingestion exceptions module provides access to exception classes that
could be raised by `dminer` parsers.
"""

class DataStoreNotSpecifiedError(Exception):
    """
    The `dminer.ingestion.base.exceptions.DataStoreNotSpecifiedError` is raised
    when an ingestion point is not provided a datastore to use with the ingestion
    point.
    """
    pass
