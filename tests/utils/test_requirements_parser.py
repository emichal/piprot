import unittest
from unittest import mock

from piprot.models import Requirement
from piprot.utils.requirements_parser import RequirementsParser


class ParseRequirementsFileTest(unittest.TestCase):
    def test_parses_file_correctly(self):
        expected_requirements = [
            Requirement("test", "1.0.0", False),
            Requirement("recursed-requirement", "0.0.1", False),
            Requirement("ignored-requirement", "0.1.0", True),
            Requirement("ignored-requirement2", "0.2.0", True),
            Requirement("ignored-requirement3", "0.3.0", True),
        ]

        actual_requirements = RequirementsParser("tests/utils/fixtures/requirements.txt").parse()

        self.assertListEqual(actual_requirements, expected_requirements)

    def test_doesnt_go_infinite_loop(self):
        expected_requirements = [
            Requirement("do-not", "0.0.1", False),
            Requirement("go-infinite", "0.0.2", False),
        ]

        actual_requirements = RequirementsParser(
            "tests/utils/fixtures/requirements-infinite.txt"
        ).parse()

        self.assertListEqual(actual_requirements, expected_requirements)
