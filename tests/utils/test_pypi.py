import unittest

from piprot.models import Requirement
from piprot.utils.pypi import PypiPackageInfoDownloader


class PypiPackageInfoDownloaderTest(unittest.TestCase):
    def test_fresh_package(self):
        downloader = PypiPackageInfoDownloader()
        r = Requirement("requests", "", False)
        version, release_date = downloader.version_and_release_date(r)

        r2 = Requirement("requests", str(version), False)
        version2, release_date2 = downloader.version_and_release_date(r2)

        self.assertEqual(version, version2)
        self.assertEqual(release_date, release_date2)

    def test_rotten_package(self):
        downloader = PypiPackageInfoDownloader()
        r = Requirement("requests", "1.1.0", False)
        version, release_date = downloader.version_and_release_date(r)

        r2 = Requirement("requests", "", False)
        version2, release_date2 = downloader.version_and_release_date(r2)

        self.assertNotEqual(version, version2)
        self.assertNotEqual(release_date, release_date2)

