class PatientNotFoundException(Exception):
    """Raised when a patient record cannot be found."""
    pass

class InvalidRequestException(Exception):
    """Raised when a request is invalid due to missing or malformed data."""
    pass

class DatabaseIntegrityError(Exception):
    """Raised when a database operation violates integrity constraints."""
    pass

class InternalServerError(Exception):
    """Raised for unexpected server-side errors."""
    pass

class DatabaseIntegrityError(Exception):
    pass
class ValueError(Exception):
    pass
class TypeError(Exception):
    pass
class Exception(Exception):
    pass
class PatientDeletionError(Exception):
    pass