import re
from typing import List, Tuple, Optional

PRERELEASE_REGEX = re.compile(r"(a|b|c|rc|alpha|beta|pre|preview|dev|svn|git)")


class PiprotVersion:
    def __init__(self, version: str) -> None:
        self.version = version
        self.parts = self.__version_to_parts()

    def is_direct_successor(self, other: "PiprotVersion") -> bool:
        if len(self.parts) != len(other.parts):
            return False

        return all(
            self.parts[index] - other.parts[index] <= 1
            for index, diff
            in enumerate(self.parts)
        )

    def __str__(self) -> str:  # pragma: no cover
        return str(self.version)

    def __cmp__(self, to_compare: "PiprotVersion") -> int:
        if self.version == to_compare.version:
            return 0

        our_parts = self.parts
        parts_to_compare = to_compare.parts

        # ensure both _parts_ lists have the same length
        our_parts, parts_to_compare = PiprotVersion.align_parts(
            our_parts, parts_to_compare
        )

        if self.is_prerelease():
            return 1
        if to_compare.is_prerelease():
            return -1

        for us, them in zip(self.parts, to_compare.parts):
            if us != them:
                return us - them
        return 0

    def __lt__(self, other: "PiprotVersion") -> bool:
        return self.__cmp__(other) < 0

    def __gt__(self, other: "PiprotVersion") -> bool:
        return self.__cmp__(other) > 0

    def __eq__(self, other: "PiprotVersion") -> bool:
        return self.__cmp__(other) == 0

    def is_prerelease(self):
        return bool(PRERELEASE_REGEX.search(self.version))

    def __version_to_parts(self) -> List[int]:
        version = self.version.strip().replace("-", ".")
        parts = version.split(".")
        return [int(re.sub(r"\D", "", part) or 0) for part in parts]

    @staticmethod
    def align_parts(
        first_parts: List[int], second_parts: List[int]
    ) -> Tuple[List[int], List[int]]:
        while len(first_parts) > len(second_parts):
            second_parts.append(0)
        while len(second_parts) > len(first_parts):
            first_parts.append(0)
        return first_parts, second_parts
