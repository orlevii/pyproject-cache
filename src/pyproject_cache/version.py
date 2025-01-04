from __future__ import annotations


def __get_runtime_version() -> str | None:
    import importlib.metadata

    try:
        return importlib.metadata.version("pyproject-cache")
    except importlib.metadata.PackageNotFoundError:
        return None


__version__ = __get_runtime_version()
