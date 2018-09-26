import logging
import requests

from datetime import datetime, date
from piprot.models import Requirement, PiprotVersion

from typing import Tuple, Optional


logger = logging.getLogger(__name__)


class PypiPackageInfoDownloader:
    PYPI_BASE_URL = "https://pypi.org/pypi"

    def version_and_release_date(
        self, requirement: Requirement
    ) -> Tuple[Optional[PiprotVersion], Optional[date]]:

        info = self._get_info_from_pypi(requirement)
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

    def _extract_release_date(
        self, info: dict, version: PiprotVersion
    ) -> Optional[date]:
        try:
            release_date = info["releases"][str(version)][0]["upload_time"]
        except (KeyError, IndexError):
            logger.error(f"Error while processing {info}. No upload time available.")
            return None
        return datetime.strptime(release_date, "%Y-%m-%dT%H:%M:%S").date()

    def _get_info_from_pypi(self, requirement: Requirement) -> Optional[dict]:
        info_response = self.__get_info_from_pypi(requirement)
        if not info_response:
            return None

        try:
            info = info_response.json()
        except ValueError as e:
            logger.error(
                f"Cannot decode json response from PyPI for package {requirement.package}. "
                f"Error: {e}."
            )
            return None
        return info

    def __get_info_from_pypi(
        self, requirement: Requirement
    ) -> Optional[requests.Response]:
        url = PypiPackageInfoDownloader.pypi_url(requirement)
        try:
            response = requests.get(url)
            if response.status_code == 404:
                response = self._handle_404(response, url)
        except requests.HTTPError as e:
            logger.error(
                f"Couldn't get PyPI info for package: {requirement.package}. Error: {e}"
            )
            return None
        return response

    def _handle_404(self, response: requests.Response, url: str) -> Optional[requests.Response]:
        root_url = url.rpartition("/")[0]
        res = requests.head(root_url)
        if res.status_code == 301:
            new_location = f"{res.headers['location']}/json"
            return requests.get(new_location)
        return None

    @classmethod
    def pypi_url(cls, requirement: Requirement) -> str:
        if requirement.version:
            return (
                f"{cls.PYPI_BASE_URL}/{requirement.package}/{requirement.version}/json"
            )
        return f"{cls.PYPI_BASE_URL}/{requirement.package}/json"
