import logging

import aiohttp

from datetime import datetime, date
from piprot.models import Requirement, PiprotVersion

from typing import Tuple, Optional


logger = logging.getLogger(__name__)


class PypiPackageInfoDownloader:
    PYPI_BASE_URL = "https://pypi.org/pypi"

    async def version_and_release_date(
        self, requirement: Requirement
    ) -> Tuple[Optional[PiprotVersion], Optional[date]]:

        info = await self._get_info_from_pypi(requirement)
        if not info:
            return None

        if not requirement.version:
            version = self._extract_version_from_response(info)
        else:
            version = PiprotVersion(requirement.version)
        release_date = self._extract_release_date(info, version)
        return version, release_date

    def _extract_version_from_response(self, info: dict) -> PiprotVersion:
        version = info["info"].get("stable_version")
        if version:
            return PiprotVersion(version)

        all_versions = [PiprotVersion(v) for v in info["releases"].keys()]
        stable_versions = list(filter(lambda v: not v.is_prerelease(), all_versions))
        if stable_versions:
            version = max(stable_versions)
        else:
            # if there are no stable versions, try with a prereleases
            version = max(all_versions)
        return version

    def _extract_release_date(self, info: dict, version: PiprotVersion) -> Optional[date]:
        try:
            release_date = info["releases"][str(version)][0]["upload_time"]
        except (KeyError, IndexError):
            name = info["info"].get("name")
            logger.error(
                f"Failed to extract release date for version: {name} {version}. "
                f"No upload time available."
            )
            return None
        return datetime.strptime(release_date, "%Y-%m-%dT%H:%M:%S").date()

    async def _get_info_from_pypi(self, requirement: Requirement) -> Optional[dict]:
        url = PypiPackageInfoDownloader.pypi_url(requirement)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 404:
                        return await self._handle_404(response, url)
                    return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"Couldn't get PyPI info for package: {requirement.package}. Error: {e}")
            return None

    async def _handle_404(self, response: aiohttp.ClientResponse, url: str) -> Optional[dict]:
        root_url = url.rpartition("/")[0]
        async with aiohttp.ClientSession() as session:
            async with session.head(root_url) as res:
                if res.status == 301:
                    new_location = f"{res.headers['location']}/json"
                    return await session.get(new_location).json()
        return None

    @classmethod
    def pypi_url(cls, requirement: Requirement) -> str:
        if requirement.version:
            return f"{cls.PYPI_BASE_URL}/{requirement.package}/{requirement.version}/json"
        return f"{cls.PYPI_BASE_URL}/{requirement.package}/json"
