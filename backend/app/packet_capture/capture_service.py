import threading
from collections.abc import Callable
from app.packet_capture.exceptions import (
    CaptureAlreadyRunningError,
    CaptureNotRunningError,
    InterfaceUnavailableError,
    PermissionDeniedError,
)
from app.packet_capture.flow_tracker import FlowTracker
from app.packet_capture.interface_manager import validate_interface
from app.packet_capture.packet_parser import parse_packet
from app.packet_capture.schemas import CaptureStatus

class CaptureService:
    def __init__(self) -> None:
        self._running = False
        self._interface: str | None = None
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._packet_count = 0
        self._flow_tracker = FlowTracker()
        self._callback: Callable | None = None

    @property
    def running(self) -> bool:
        return self._running

    @property
    def flow_tracker(self) -> FlowTracker:
        return self._flow_tracker

    def set_packet_callback(self, callback: Callable) -> None:
        self._callback = callback

    def status(self) -> CaptureStatus:
        if not self._scapy_available():
            return CaptureStatus(available=False, reason="Packet capture requires local network interface permission")
        return CaptureStatus(
            available=True,
            running=self._running,
            interface=self._interface,
            packets_captured=self._packet_count,
        )

    def start_capture(self, interface: str) -> None:
        if self._running:
            raise CaptureAlreadyRunningError(f"Capture already running on {self._interface}")
        validate_interface(interface)
        self._stop_event.clear()
        self._packet_count = 0
        self._flow_tracker.reset()
        self._interface = interface
        self._running = True
        self._thread = threading.Thread(target=self._capture_loop, args=(interface,), daemon=True)
        self._thread.start()

    def stop_capture(self) -> None:
        if not self._running:
            raise CaptureNotRunningError("No capture is running")
        self._stop_event.set()
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        self._thread = None
        self._interface = None

    def _capture_loop(self, interface: str) -> None:
        try:
            from scapy.sendrecv import sniff
        except ImportError:
            self._running = False
            raise PermissionDeniedError("Scapy is not installed")

        try:
            sniff(
                iface=interface,
                prn=self._process_packet,
                stop_filter=lambda _: self._stop_event.is_set(),
                store=False,
            )
        except PermissionError as exc:
            self._running = False
            raise PermissionDeniedError("OS-level capture permission denied") from exc
        except Exception as exc:
            self._running = False
            raise InterfaceUnavailableError(f"Capture failed: {exc}") from exc

    def _process_packet(self, packet) -> None:
        if self._stop_event.is_set():
            return
        meta = parse_packet(packet, self._interface or "unknown")
        if meta is None:
            return
        self._packet_count += 1
        self._flow_tracker.aggregate_flow(meta)
        if self._callback:
            self._callback(meta)

    @staticmethod
    def _scapy_available() -> bool:
        try:
            import scapy  # noqa: F401
            return True
        except ImportError:
            return False


capture_service = CaptureService()
