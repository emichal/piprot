import unittest

from piprot.models import Requirement, NotFrozenRequirement


class RequirementTest(unittest.TestCase):
    def test_creates_requirement_object_from_clean_line(self):
        line = "test==1.0.0"
        requirement = Requirement.from_line(line)
        self.assertEqual(requirement.package, "test")
        self.assertEqual(requirement.version, "1.0.0")
        self.assertFalse(requirement.ignore)

    def test_strips_comments_from_line(self):
        line = "test2==2.0.0  # cool kids write tests"
        requirement = Requirement.from_line(line)
        self.assertEqual(requirement.package, "test2")
        self.assertEqual(requirement.version, "2.0.0")
        self.assertFalse(requirement.ignore)

    def test_checks_for_norot_comment(self):
        line = "test3==3.0.0  # norot"
        requirement = Requirement.from_line(line)
        self.assertEqual(requirement.package, "test3")
        self.assertEqual(requirement.version, "3.0.0")
        self.assertTrue(requirement.ignore)

    def test_checks_for_norot_comment_with_space(self):
        line = "test4==4.0.0  # no rot"
        requirement = Requirement.from_line(line)
        self.assertEqual(requirement.package, "test4")
        self.assertEqual(requirement.version, "4.0.0")
        self.assertTrue(requirement.ignore)

    def test_raises_exception_on_invalid_line(self):
        invalid_line = "this is an invalid requirement line"
        with self.assertRaises(NotFrozenRequirement):
            Requirement.from_line(invalid_line)
