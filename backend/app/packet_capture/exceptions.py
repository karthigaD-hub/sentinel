class CaptureError(Exception):
    pass

class PermissionDeniedError(CaptureError):
    pass

class InvalidInterfaceError(CaptureError):
    pass

class InterfaceUnavailableError(CaptureError):
    pass

class CaptureAlreadyRunningError(CaptureError):
    pass

class CaptureNotRunningError(CaptureError):
    pass
