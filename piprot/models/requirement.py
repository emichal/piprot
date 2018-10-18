import re

from dataclasses import dataclass
from piprot.utils.requirements import remove_comments
from typing import NamedTuple


REQUIREMENT_REGEX = re.compile(r"\s*(?P<package>[^\s\[\]]+)(?P<extras>\[\S+\])?==(?P<version>\S+)")
NOROT_REGEX = re.compile(r"^.*?\s+#\s*no\s?rot\s*$")


class NotFrozenRequirement(Exception):
    pass


@dataclass
class Requirement:
    package: str
    version: str = ""
    ignore: bool = False

    @staticmethod
    def from_line(line: str) -> "Requirement":
        ignore = bool(NOROT_REGEX.fullmatch(line))

        # ignore comments (part after #) and clean whitespace
        clean_line = remove_comments(line)
        match = REQUIREMENT_REGEX.fullmatch(clean_line)

        if not match:
            raise NotFrozenRequirement(f"Line: '{line}' does not contain frozen requirement.")

        package = match.group("package")
        version = match.group("version")

        return Requirement(package, version, ignore)
