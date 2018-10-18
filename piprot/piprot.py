import asyncio
import argparse
import logging
import os
import sys

from datetime import timedelta, date
from typing import List, Optional

from . import __version__

from piprot.models import Requirement
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
        logger.error(f"Ignoring updates for {requirement.package}.")
        return False

    if not all([latest_version, current_version]):
        logger.error(
            f"Skipping {requirement.package} ({requirement.version}). "
            "Cannot fetch info from PyPI"
        )
        return False

    if latest_version > current_version:
        if not latest_version.is_direct_successor(current_version):
            if not all([latest_release_date, current_release_date]):
                logger.warning(
                    f"{requirement.package}. ({str(current_version)}) "
                    f"is out of date. No delay info available. "
                    f"Latest version is: {latest_version} "
                )
                return True

            rotten_time = calculate_rotten_time(latest_release_date, current_release_date)
            if rotten_time > delay_timedelta:
                release_rotten_time = calculate_rotten_time(latest_release_date)
                logger.error(
                    f"{requirement.package} ({str(current_version)}) "
                    f"is {rotten_time.days} days out of date. "
                    f"Latest version is: {latest_version} "
                    f"({release_rotten_time.days} days old)."
                )
                return True
        else:
            _time_delta = calculate_rotten_time(latest_release_date)
            if _time_delta > delay_timedelta:
                logger.error(
                    f"{requirement.package} ({str(current_version)}) "
                    f"is {_time_delta.days} days out of date. "
                    f"Latest version is: {latest_version}"
                )
                return True
    logger.error(f"{requirement.package} ({str(current_version)}) is up to date")
    return False


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
