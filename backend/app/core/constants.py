from enum import StrEnum

class RoleName(StrEnum):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"

class PermissionName(StrEnum):
    DASHBOARD_VIEW = "dashboard:view"
    CAPTURE_VIEW = "capture:view"
    CAPTURE_START = "capture:start"
    CAPTURE_STOP = "capture:stop"
    DETECTION_VIEW = "detection:view"
    ALERTS_VIEW = "alerts:view"
    ALERTS_UPDATE = "alerts:update"
    THREATINTEL_VIEW = "threatintel:view"
    ASSISTANT_USE = "assistant:use"
    REPORTS_VIEW = "reports:view"
    QUANTUM_VIEW = "quantum:view"
    SETTINGS_VIEW = "settings:view"
    SETTINGS_UPDATE = "settings:update"
    ADMIN_MANAGE = "admin:manage"

ALL_PERMISSIONS = [item.value for item in PermissionName]
