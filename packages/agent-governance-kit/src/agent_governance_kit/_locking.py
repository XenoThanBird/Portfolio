"""Internal cross-platform interprocess file lock.

Used to serialize read-check-write critical sections in the audit log
and the HITL gate. Locks a dedicated ``*.lock`` file (never the data
file itself) so lock acquisition cannot interfere with atomic replaces
of the data.
"""

from __future__ import annotations

import sys
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


class LockTimeoutError(TimeoutError):
    """Raised when an interprocess lock cannot be acquired in time."""


if sys.platform == "win32":
    import msvcrt

    def _try_lock(fileno: int) -> bool:
        try:
            msvcrt.locking(fileno, msvcrt.LK_NBLCK, 1)
            return True
        except OSError:
            return False

    def _unlock(fileno: int) -> None:
        msvcrt.locking(fileno, msvcrt.LK_UNLCK, 1)

else:
    import fcntl

    def _try_lock(fileno: int) -> bool:
        try:
            fcntl.flock(fileno, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except OSError:
            return False

    def _unlock(fileno: int) -> None:
        fcntl.flock(fileno, fcntl.LOCK_UN)


@contextmanager
def interprocess_lock(lock_path: Path, timeout: float = 10.0) -> Iterator[None]:
    """Hold an exclusive lock on ``lock_path`` for the with-block.

    Blocks (polling) until acquired or ``timeout`` elapses, then raises
    :class:`LockTimeoutError`.
    """
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    f = open(lock_path, "a+b")
    acquired = False
    try:
        f.seek(0)
        deadline = time.monotonic() + timeout
        while not acquired:
            acquired = _try_lock(f.fileno())
            if not acquired:
                if time.monotonic() >= deadline:
                    raise LockTimeoutError(f"could not acquire lock {lock_path}")
                time.sleep(0.01)
        yield
    finally:
        if acquired:
            f.seek(0)
            _unlock(f.fileno())
        f.close()
