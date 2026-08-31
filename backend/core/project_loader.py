"""
project_loader.py

Safe handling of uploaded ZIP archives.

Security boundaries enforced here:
  - maximum upload size
  - maximum number of extracted files
  - maximum total extracted size (zip-bomb protection)
  - only allowed source extensions are read for analysis
  - path traversal protection (../, absolute paths, drive letters)
  - extraction into an isolated temp directory
  - uploaded code is NEVER executed
  - caller is responsible for calling cleanup() when done
"""

from __future__ import annotations

import os
import shutil
import tempfile
import zipfile
from dataclasses import dataclass, field
from typing import List


MAX_UPLOAD_SIZE_BYTES = 20 * 1024 * 1024        # 20 MB compressed
MAX_EXTRACTED_FILES = 2000
MAX_TOTAL_EXTRACTED_SIZE = 100 * 1024 * 1024    # 100 MB uncompressed
MAX_SINGLE_FILE_SIZE = 5 * 1024 * 1024          # 5 MB per file

ALLOWED_SOURCE_EXTENSIONS = {".py"}


class ProjectLoadError(Exception):
    """Raised when an uploaded archive fails safety validation."""


@dataclass
class LoadedProject:
    root_dir: str
    python_files: List[str] = field(default_factory=list)  # absolute paths
    rejected_entries: List[str] = field(default_factory=list)

    def relative_path(self, abs_path: str) -> str:
        return os.path.relpath(abs_path, self.root_dir).replace(os.sep, "/")

    def cleanup(self) -> None:
        shutil.rmtree(self.root_dir, ignore_errors=True)


def _is_safe_member_path(name: str) -> bool:
    """Reject absolute paths, drive letters, and path traversal segments."""
    if not name or name.startswith("/") or name.startswith("\\"):
        return False
    # Windows drive letter e.g. C:\
    if len(name) > 1 and name[1] == ":":
        return False
    normalized = os.path.normpath(name)
    if normalized.startswith("..") or os.path.isabs(normalized):
        return False
    parts = normalized.split(os.sep)
    if ".." in parts:
        return False
    return True


def load_zip_bytes(data: bytes) -> LoadedProject:
    """
    Validate and safely extract an in-memory ZIP archive.
    Only .py files are extracted for analysis; everything else is skipped.
    Uploaded code is never executed at any point in this process.
    """
    if len(data) == 0:
        raise ProjectLoadError("Uploaded file is empty.")

    if len(data) > MAX_UPLOAD_SIZE_BYTES:
        raise ProjectLoadError(
            f"Uploaded archive exceeds the maximum allowed size "
            f"({MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)} MB)."
        )

    import io
    try:
        zf = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile as exc:
        raise ProjectLoadError("Uploaded file is not a valid ZIP archive.") from exc

    infolist = zf.infolist()
    if len(infolist) > MAX_EXTRACTED_FILES:
        raise ProjectLoadError(
            f"Archive contains too many entries (limit: {MAX_EXTRACTED_FILES})."
        )

    total_uncompressed = sum(i.file_size for i in infolist)
    if total_uncompressed > MAX_TOTAL_EXTRACTED_SIZE:
        raise ProjectLoadError(
            "Archive's uncompressed size exceeds the safety limit "
            f"({MAX_TOTAL_EXTRACTED_SIZE // (1024 * 1024)} MB). Possible zip bomb."
        )

    root_dir = tempfile.mkdtemp(prefix="sentinel_ai_")
    project = LoadedProject(root_dir=root_dir)

    try:
        for info in infolist:
            name = info.filename

            if info.is_dir():
                continue

            if not _is_safe_member_path(name):
                project.rejected_entries.append(name)
                continue

            if info.file_size > MAX_SINGLE_FILE_SIZE:
                project.rejected_entries.append(name)
                continue

            _, ext = os.path.splitext(name)
            if ext.lower() not in ALLOWED_SOURCE_EXTENSIONS:
                # Not a supported source file — skip silently (not rejected,
                # just out of scope for v1 which only analyzes Python).
                continue

            dest_path = os.path.join(root_dir, name)
            dest_path = os.path.normpath(dest_path)

            # Final belt-and-braces containment check.
            if not dest_path.startswith(os.path.normpath(root_dir) + os.sep) and \
                    dest_path != os.path.normpath(root_dir):
                project.rejected_entries.append(name)
                continue

            os.makedirs(os.path.dirname(dest_path), exist_ok=True)

            with zf.open(info, "r") as src, open(dest_path, "wb") as dst:
                dst.write(src.read())

            project.python_files.append(dest_path)

    except Exception:
        project.cleanup()
        raise

    finally:
        zf.close()

    if not project.python_files:
        project.cleanup()
        raise ProjectLoadError(
            "No supported Python (.py) source files were found in the archive."
        )

    return project


def load_demo_project(demo_dir: str) -> LoadedProject:
    """
    Load the bundled demo scenario without any upload — used by
    POST /api/demo/run. Copies the sample files into an isolated temp
    directory so the same downstream pipeline code path is exercised.
    """
    root_dir = tempfile.mkdtemp(prefix="sentinel_ai_demo_")
    project = LoadedProject(root_dir=root_dir)

    for dirpath, _dirnames, filenames in os.walk(demo_dir):
        for fname in filenames:
            if not fname.endswith(".py"):
                continue
            src_path = os.path.join(dirpath, fname)
            rel = os.path.relpath(src_path, demo_dir)
            dest_path = os.path.join(root_dir, rel)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copyfile(src_path, dest_path)
            project.python_files.append(dest_path)

    if not project.python_files:
        project.cleanup()
        raise ProjectLoadError("Demo project sample files are missing.")

    return project
