import pytest

from piprot.models import Requirement
from piprot.utils.pypi import PypiPackageInfoDownloader


pytestmark = pytest.mark.asyncio


async def test_fresh_package():
    downloader = PypiPackageInfoDownloader()
    r = Requirement("requests", "", False)
    version, release_date = await downloader.version_and_release_date(r)

    r2 = Requirement("requests", str(version), False)
    version2, release_date2 = await downloader.version_and_release_date(r2)

    assert version == version2
    assert release_date == release_date2


async def test_rotten_package():
    downloader = PypiPackageInfoDownloader()
    r = Requirement("requests", "1.1.0", False)
    version, release_date = await downloader.version_and_release_date(r)

    r2 = Requirement("requests", "", False)
    version2, release_date2 = await downloader.version_and_release_date(r2)

    assert version != version2
    assert release_date != release_date2
