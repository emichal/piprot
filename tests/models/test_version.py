import unittest

from piprot.models import PiprotVersion


class PiprotVersionTest(unittest.TestCase):
    def test_same_version(self):
        v1 = PiprotVersion("1.0.0")
        v2 = PiprotVersion("1.0.0")
        self.assertTrue(v1 == v2)

    def test_same_version_dashed(self):
        v1 = PiprotVersion("1.0.0")
        v2 = PiprotVersion("1-0-0")
        self.assertTrue(v1 == v2)

    def test_less_than_operator(self):
        v1 = PiprotVersion("0.1.0")
        v2 = PiprotVersion("1.0.0")
        self.assertTrue(v1 < v2)

    def test_greater_than_operator(self):
        v1 = PiprotVersion("1.0.0")
        v2 = PiprotVersion("0.1.0")
        self.assertTrue(v1 > v2)

    def test_prerelease_is_greater(self):
        v1 = PiprotVersion("1.0.0a")
        v2 = PiprotVersion("0.9.0")
        self.assertTrue(v1 > v2)

    def test_prerelease_is_greater_other_way(self):
        v1 = PiprotVersion("0.9.0")
        v2 = PiprotVersion("1.0.0a")
        self.assertTrue(v1 < v2)

    def test_aligns_parts(self):
        v1 = PiprotVersion("1.0.1")
        v2 = PiprotVersion("1.0")
        self.assertTrue(v1 > v2)

    def test_aligns_parts_other_way(self):
        v1 = PiprotVersion("1.0")
        v2 = PiprotVersion("1.0.1")
        self.assertTrue(v1 < v2)
