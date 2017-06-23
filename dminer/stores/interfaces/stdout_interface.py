"""
TODO: IMPLEMENT
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
        TODO: IMPLEMENT
        """
        raise DatastoreOperationNotSupportedException()
    
    def delete(self, obj):
        """
        TODO: IMPLEMENT
        """
        raise DatastoreOperationNotSupportedException()
    
    def update(self, obj):
        """
        TODO: IMPLEMENT
        """
        raise DatastoreOperationNotSupportedException()
    
class DatastoreOperationNotSupportedException(object):
    """
    TODO: DOC
    """
    pass
