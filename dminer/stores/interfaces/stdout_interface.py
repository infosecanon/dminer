"""
TODO: DOC
"""

class STDOutInterface(object):
    """
    TODO: DOC
    """
    def create(self, obj):
        """
        TODO: DOC
        """
        print obj
    
    def find(self, obj):
        """
        TODO: DOC
        """
        raise DatastoreOperationNotSupportedException()
    
    def delete(self, obj):
        """
        TODO: DOC
        """
        raise DatastoreOperationNotSupportedException()
    
    def update(self, obj):
        """
        TODO: ODC
        """
        raise DatastoreOperationNotSupportedException()
    
class DatastoreOperationNotSupportedException(object):
    """
    TODO: DOC
    """
    pass
