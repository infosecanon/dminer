"""
The `dminer.ingestion.base.parser` module provides base classes for subclassing
in parsers.
"""

class BaseParser(object):
    """
    The `dminer.ingestion.base.parser.BaseParser` is a scaffold class for the
    implementation of parsers.
    """
    def parse(self):
        raise NotImplementedError("The parse function has not been implemented.")
