import asyncio
import logging
from datetime import timedelta, date
from itertools import chain
from piprot.models import Requirement, PackageInfo, Messages
from piprot.utils.pypi import PypiPackageInfoDownloader
from piprot.utils.requirements_parser import RequirementsParser
from typing import Optional, Tuple, List


logger: logging.Logger = logging.getLogger(__name__)
loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()


class Piprot:
    def __init__(self, req_files: List[str], delay_in_days: int = 5) -> None:
        self.pypi = PypiPackageInfoDownloader()
        self.delay_timedelta = timedelta(days=delay_in_days)
        self.requirements = list(
            chain.from_iterable([RequirementsParser(req_file).parse() for req_file in req_files])
        )

    def main(self) -> int:
        tasks = [self._handle_single_requirement(requirement) for requirement in self.requirements]
        has_outdated_packages = loop.run_until_complete(asyncio.gather(*tasks))
        if any(has_outdated_packages):
            return 1
        return 0

    async def _handle_single_requirement(self, requirement: Requirement) -> bool:
        current_version, current_release_date = await self.pypi.version_and_release_date(
            requirement
        )
        latest_version, latest_release_date = await self.pypi.version_and_release_date(
            Requirement(requirement.package)
        )

        package_info = PackageInfo(
            name=requirement.package,
            latest_version=latest_version,
            latest_release_date=latest_release_date,
            current_version=current_version,
            current_release_date=current_release_date,
        )

        is_outdated, message = self.__handle_single_requirement(package_info, requirement)
        logger.error(message)
        return is_outdated

    def __handle_single_requirement(
        self, package: PackageInfo, requirement: Requirement
    ) -> Tuple[bool, str]:
        package_name, latest_version, _, current_version, _ = package

        if requirement.ignore:
            message = Messages.IGNORED.format(package=requirement.package)
            return False, message

        if not all([latest_version, current_version]):
            message = Messages.CANNOT_FETCH.format(
                package=package_name, version=requirement.version
            )
            return False, message

        if latest_version > current_version:
            return self._is_rotten(package)

        message = Messages.NOT_ROTTEN.format(
            package=requirement.package, version=str(current_version)
        )
        return False, message

    def _is_rotten(self, package: PackageInfo) -> Tuple[bool, str]:
        if not package.latest_version.is_direct_successor(package.current_version):
            return self._is_not_direct_successor_rotten(package)
        return self._is_direct_successor_rotten(package)

    def _is_direct_successor_rotten(self, package: PackageInfo) -> Tuple[bool, str]:
        rotten_time = self.calculate_rotten_time(package.latest_release_date)
        if rotten_time > self.delay_timedelta:
            message = Messages.ROTTEN_DIRECT_SUCCESSOR.format(
                package=package.name,
                current_version=str(package.current_version),
                rotten_days=rotten_time.days,
                latest_version=str(package.latest_version),
            )
            return True, message

        message = Messages.NOT_ROTTEN.format(
            package=package.name, version=str(package.current_version)
        )
        return False, message

    def _is_not_direct_successor_rotten(self, package: PackageInfo) -> Tuple[bool, str]:
        if not all([package.latest_release_date, package.current_release_date]):
            # since we cannot calculate if it's actually rotten, we assume it is
            message = Messages.NO_DELAY_INFO.format(
                package=package.name,
                current_version=str(package.current_version),
                latest_version=str(package.latest_version),
            )
            return True, message

        rotten_time = self.calculate_rotten_time(
            package.latest_release_date, package.current_release_date
        )
        if rotten_time > self.delay_timedelta:
            timedelta_since_last_release = self.calculate_rotten_time(package.latest_release_date)
            message = Messages.ROTTEN_NOT_DIRECT_SUCCESSOR.format(
                package=package.name,
                current_version=str(package.latest_version),
                rotten_days=rotten_time.days,
                latest_version=str(package.latest_version),
                days_since_last_release=timedelta_since_last_release.days,
            )
            return True, message
        message = Messages.NOT_ROTTEN.format(
            package=package.name, version=str(package.current_version)
        )
        return False, message

    @staticmethod
    def calculate_rotten_time(
        latest_release_date: date, current_release_date: Optional[date] = None
    ) -> timedelta:
        if current_release_date:
            return latest_release_date - current_release_date
        return date.today() - latest_release_date
