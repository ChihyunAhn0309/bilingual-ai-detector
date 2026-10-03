"""Cross-process advisory lock held by the actual English model worker."""
from contextlib import contextmanager
import os
from pathlib import Path
import tempfile


@contextmanager
def runtime_lock(path=None):
    lock_path = Path(path) if path else Path(tempfile.gettempdir()) / 'bilingual-ai-detector-english.lock'
    with lock_path.open('a+b') as handle:
        if handle.seek(0, os.SEEK_END) == 0:
            handle.write(b'0')
            handle.flush()
        handle.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise ValueError('Another English CLI worker is running. Retry after it completes; no score was produced.') from exc
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == 'nt':
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
