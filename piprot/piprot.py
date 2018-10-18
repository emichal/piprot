import asyncio
import argparse
import logging
import os
import sys

from datetime import timedelta, date
from typing import List, Tuple, Optional

from . import __version__

from piprot.models import Requirement, Messages, PiprotResult
from piprot.utils.requirements_parser import RequirementsParser
from piprot.utils.pypi import PypiPackageInfoDownloader


VERSION = __version__
logger = logging.getLogger(__name__)
loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()


def calculate_rotten_time(
    latest_release_date: date, current_release_date: Optional[date] = None
) -> timedelta:
    if current_release_date:
        return latest_release_date - current_release_date
    return date.today() - latest_release_date


async def handle_single_requirement(
    requirement: Requirement, delay_timedelta: timedelta, pypi_downloader: PypiPackageInfoDownloader
) -> bool:
    current_version, current_release_date = await pypi_downloader.version_and_release_date(
        requirement
    )
    latest_version, latest_release_date = await pypi_downloader.version_and_release_date(
        Requirement(requirement.package)
    )

    if requirement.ignore:
        logger.error(Messages.IGNORED.format(package=requirement.package))
        return False

    if not all([latest_version, current_version]):
        logger.error(
            Messages.CANNOT_FETCH.format(package=requirement.package, version=requirement.version)
        )
        return False

    result = PiprotResult(
        requirement,
        latest_version=latest_version,
        latest_release_date=latest_release_date,
        current_version=current_version,
        current_release_date=current_release_date,
    )

    if latest_version > current_version:
        is_rotten, message = _is_rotten(result, delay_timedelta)
        logger.error(message)
        return is_rotten

    logger.error(
        Messages.NOT_ROTTEN.format(package=requirement.package, version=str(current_version))
    )
    return False


def _is_rotten(result: PiprotResult, delay_timedelta: timedelta) -> Tuple[bool, str]:
    if not result.latest_version.is_direct_successor(result.current_version):
        return _is_not_direct_successor_rotten(result, delay_timedelta)
    return _is_direct_successor_rotten(result, delay_timedelta)


def _is_direct_successor_rotten(
    result: PiprotResult, delay_timedelta: timedelta
) -> Tuple[bool, str]:
    rotten_time = calculate_rotten_time(result.latest_release_date)
    if rotten_time > delay_timedelta:
        message = Messages.ROTTEN_DIRECT_SUCCESSOR.format(
            package=result.requirement.package,
            current_version=str(result.current_version),
            rotten_days=rotten_time.days,
            latest_version=str(result.latest_version),
        )
        return True, message
    message = Messages.NOT_ROTTEN.format(
        package=result.requirement.package, version=str(result.current_version)
    )
    return False, message


def _is_not_direct_successor_rotten(
    result: PiprotResult, delay_timedelta: timedelta
) -> Tuple[bool, str]:
    if not all([result.latest_release_date, result.current_release_date]):
        # since we cannot calculate if it's actually rotten, we assume it is
        message = Messages.NO_DELAY_INFO.format(
            package=result.requirement.package,
            current_version=str(result.current_version),
            latest_version=str(result.latest_version),
        )
        return True, message

    rotten_time = calculate_rotten_time(result.latest_release_date, result.current_release_date)
    if rotten_time > delay_timedelta:
        timedelta_since_last_release = calculate_rotten_time(result.latest_release_date)
        message = Messages.ROTTEN_NOT_DIRECT_SUCCESSOR.format(
            package=result.requirement.package,
            current_version=str(result.latest_version),
            rotten_days=rotten_time.days,
            latest_version=str(result.latest_version),
            days_since_last_release=timedelta_since_last_release.days,
        )
        return True, message
    message = Messages.NOT_ROTTEN.format(
        package=result.requirement.package, version=str(result.current_version)
    )
    return False, message


async def main(req_files: List[str], delay: int = 5) -> None:
    requirements: List[Requirement] = []
    delay_timedelta = timedelta(days=delay)

    for req_file in req_files:
        requirements.extend(RequirementsParser(req_file).parse())

    has_outdated_packages: bool = False
    downloader = PypiPackageInfoDownloader()

    has_outdated_packages = [
        await handle_single_requirement(requirement, delay_timedelta, downloader)
        for requirement in requirements
    ]

    if any(has_outdated_packages):
        sys.exit(1)
    sys.exit(0)


def piprot():
    """Parse the command line arguments and jump into the piprot() function
    (unless the user just wants the post request hook).
    """
    cli_parser = argparse.ArgumentParser(
        epilog="Here's hoping your requirements are nice and fresh!"
    )

    cli_parser.add_argument(
        "-d",
        "--delay",
        type=int,
        default=5,
        help=("Delay before an outdated package triggers an error. " "(in days, defaults to 5)."),
    )

    nargs = "+"

    if os.path.isfile("requirements.txt"):
        nargs = "*"
        default = ["requirements.txt"]
    else:
        default = None

    cli_parser.add_argument(
        "files", nargs=nargs, type=str, default=default, help="requirements file(s)"
    )

    cli_args = cli_parser.parse_args()
    # call the main function to kick off the real work
    loop.run_until_complete(main(req_files=cli_args.files, delay=cli_args.delay))


if __name__ == "__main__":
    piprot()
