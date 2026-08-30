from app.packet_capture.exceptions import (
    InvalidInterfaceError,
    InterfaceUnavailableError,
    PermissionDeniedError,
)

def list_interfaces() -> list[dict[str, str]]:
    try:
        from scapy.arch import get_if_list
        from scapy.arch.linux import get_if_addr
    except ImportError as exc:
        raise PermissionDeniedError("Scapy is not installed") from exc

    try:
        iface_list = list(get_if_list())
    except Exception as exc:
        raise InterfaceUnavailableError("Unable to enumerate network interfaces") from exc

    interfaces: list[dict[str, str]] = []
    for name in iface_list:
        try:
            addr = get_if_addr(name)
        except Exception:
            addr = ""
        interfaces.append({"name": name, "address": addr})
    return interfaces


def validate_interface(interface: str) -> None:
    if not interface or not interface.strip():
        raise InvalidInterfaceError("Interface name cannot be empty")
    try:
        from scapy.arch import get_if_list
    except ImportError as exc:
        raise PermissionDeniedError("Scapy is not installed") from exc
    try:
        available = list(get_if_list())
    except Exception as exc:
        raise InterfaceUnavailableError("Unable to enumerate network interfaces") from exc
    if interface not in available:
        raise InvalidInterfaceError(f"Interface '{interface}' not found. Available: {available}")
