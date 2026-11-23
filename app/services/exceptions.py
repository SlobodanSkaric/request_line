class ServiceException(Exception):
    """Base class for all exceptions raised by this module."""

class NotFoundError(ServiceException):
    def __init__(self, entity: str, entity_id: object) -> None:
        self.entity = entity
        self.entity_id = entity_id
        super().__init__(f"{entity} not found {entity_id}")

class ConflictError(ServiceException):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

class ValidationError(ServiceException):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

class ForbiddenError(ServiceException):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


"""Return Exceptions because same service call works,cli etc"""