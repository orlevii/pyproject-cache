from pathlib import Path
from typing import Any

import toml
from swiftcli import BaseCommand
from swiftcli.types import Flag
from swiftcli.command import CommandConfig

from pyproject_cache.logger import logger

from .common_params import CommonParams

StrDict = dict[str, Any]


class CleanParams(CommonParams):
    dry_run: Flag = False


class CleanCommand(BaseCommand[CleanParams]):
    NAME = "prepare"
    CONFIG = CommandConfig(
        help="""
        Cleans redundant sections that are not needed for dependency installation
        """
    )

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.cwd = Path()

    def run(self) -> None:
        pyproject_toml_files = self._list_pyproject_files()
        if not pyproject_toml_files:
            logger.warning("No pyproject.toml files found")
            return
        poetry_lock_files = self._list_poetry_lock_files()

        for path in pyproject_toml_files:
            pyproject_toml = self._clean_pyproject(path)
            if not self.params.dry_run:
                path.write_text(toml.dumps(pyproject_toml))

        self._keep_only(pyproject_toml_files + poetry_lock_files)

    def _list_pyproject_files(self) -> list[Path]:
        return list(self.cwd.glob("**/pyproject.toml"))

    def _list_poetry_lock_files(self) -> list[Path]:
        return list(self.cwd.glob("**/poetry.lock"))

    def _clean_pyproject(self, path: Path) -> StrDict:
        with path.open() as f:
            pyproject = toml.load(f)
            tool_poetry = pyproject.get("tool", {}).get("poetry", {})
            tool_poetry = self._clean_redundant_field(tool_poetry)
            self._modify_tool_poetry(tool_poetry)
            return self._to_pyproject(tool_poetry)

    @staticmethod
    def _clean_redundant_field(tool_poetry: StrDict) -> StrDict:
        relevant_fields = [
            "name",
            "version",
            "description",
            "authors",
            "dependencies",
            "group",
        ]
        return {
            field: tool_poetry.get(field)
            for field in relevant_fields
            if field in tool_poetry
        }

    @staticmethod
    def _modify_tool_poetry(tool_poetry: StrDict) -> None:
        tool_poetry["name"] = "dummy"
        tool_poetry["version"] = "0.1.0"
        tool_poetry["description"] = ""
        tool_poetry["authors"] = "Dummy <dummy@example.com>"

    @staticmethod
    def _to_pyproject(tool_poetry: StrDict) -> StrDict:
        return {"tool": {"poetry": tool_poetry}}

    def _keep_only(self, paths: list[Path]) -> None:
        paths_set = set((str(p) for p in paths))

        all_paths: list[Path] = list(self.cwd.glob("**/*"))
        all_files = [p for p in all_paths if p.is_file()]
        files_to_delete = [p for p in all_files if str(p) not in paths_set]

        for file in files_to_delete:
            if self.params.dry_run:
                print(f"[DRYRUN] Deleting {file}")
