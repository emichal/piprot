import os

from io import FileIO
from typing import List, Tuple

from piprot.models import Requirement, NotFrozenRequirement
from piprot.utils.requirements import remove_comments


class RequirementsParser:
    def __init__(self, requirements_filename: str) -> None:
        self.requirements_filename = requirements_filename

    def parse(self) -> List[Requirement]:
        with open(self.requirements_filename, "r") as file:
            requirements, to_recurse = self._parse_file(file)

        for filename in to_recurse:
            filename = self._clean_recursive_requirements_line(filename)
            full_path = self._get_recursive_requirement_file_full_path(filename)
            with open(full_path, "r") as file:
                recursed_requirements, _ = self._parse_file(file)
            requirements.extend(recursed_requirements)
        return requirements

    def _parse_file(self, file: FileIO) -> Tuple[List[Requirement], List[str]]:
        requirements: List[Requirement] = []
        to_recurse: List[str] = []

        for line in file.readlines():
            try:
                requirements.append(Requirement.from_line(line))
            except NotFrozenRequirement:
                if line.startswith("-r "):
                    to_recurse.append(remove_comments(line))
                else:
                    continue
        return requirements, to_recurse

    def _clean_recursive_requirements_line(self, line: str) -> str:
        # we're sure that the line starts with "-r ", so we're
        # just stripping first 3 characters
        return line[3:]

    def _get_recursive_requirement_file_full_path(
        self, requirements_file_to_recurse_filename: str
    ) -> str:
        base_dir = os.path.dirname(os.path.abspath(self.requirements_filename))
        return os.path.join(base_dir, requirements_file_to_recurse_filename)
