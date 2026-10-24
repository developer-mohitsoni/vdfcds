import json
from pathlib import Path
from threading import Lock

from pydantic import ValidationError

from app.models import WindSnapshot


class SnapshotUnavailableError(RuntimeError):
    """Raised when the processed snapshot cannot be loaded or validated."""


class SnapshotRepository:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._cached: WindSnapshot | None = None
        self._cached_mtime_ns: int | None = None
        self._lock = Lock()

    def load(self) -> WindSnapshot:
        try:
            modified_ns = self.path.stat().st_mtime_ns
        except OSError as error:
            raise SnapshotUnavailableError(f"Snapshot not found at {self.path}") from error

        with self._lock:
            if self._cached is not None and self._cached_mtime_ns == modified_ns:
                return self._cached
            try:
                payload = json.loads(self.path.read_text(encoding="utf-8"))
                snapshot = WindSnapshot.model_validate(payload)
            except (OSError, json.JSONDecodeError, ValidationError) as error:
                raise SnapshotUnavailableError(
                    f"Snapshot at {self.path} is unreadable or invalid"
                ) from error
            self._cached = snapshot
            self._cached_mtime_ns = modified_ns
            return snapshot
