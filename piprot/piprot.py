""" piprot - How rotten are your requirements?  """
import argparse
import logging
import os
import sys

from datetime import timedelta, date
from typing import List

from . import __version__

from piprot.models import Requirement, PiprotResult
from piprot.utils.requirements_parser import RequirementsParser
from piprot.utils.pypi import PypiPackageInfoDownloader


VERSION = __version__
logger = logging.getLogger(__name__)


def calculate_rotten_time(
    result: PiprotResult, between_releases: bool = False
) -> timedelta:
    if between_releases:
        return result.latest_release_date - result.current_release_date
    return date.today() - result.latest_release_date


def main(
    req_files: List[str],
    delay: int = 5,
    calculate_rotten_between_releases: bool = False,
) -> None:
    requirements: List[Requirement] = []
    delay_timedelta = timedelta(days=delay)

    for req_file in req_files:
        requirements.extend(RequirementsParser(req_file).parse())

    results: List[PiprotResult] = []
    has_outdated_packages: bool = False
    downloader = PypiPackageInfoDownloader()

    for requirement in requirements:
        current_version, current_release_date = downloader.version_and_release_date(
            requirement
        )
        latest_version, latest_release_date = downloader.version_and_release_date(
            Requirement(requirement.package)
        )

        results.append(
            PiprotResult(
                requirement,
                latest_version,
                latest_release_date,
                current_version,
                current_release_date,
            )
        )

    for result in results:
        if result.requirement.ignore:
            logger.error(f"Ignoring updates for {result.requirement.package}.")
            continue

        if result.current_version != result.latest_version:
            if calculate_rotten_between_releases:
                if not all([result.latest_release_date, result.current_release_date]):
                    logger.warning(
                        f"Cannot calculate days out of date for {result.requirement.package}"
                    )
                else:
                    _time_delta = calculate_rotten_time(result, between_releases=True)
                    if _time_delta > delay_timedelta:
                        has_outdated_packages = True
                        logger.error(
                            f"{result.requirement.package} ({str(result.current_version)}) "
                            f"is {_time_delta.days} out of date. "
                            f"Latest version is: {result.latest_version}"
                        )
            else:
                _time_delta = calculate_rotten_time(result, between_releases=False)
                if _time_delta > delay_timedelta:
                    has_outdated_packages = True
                    logger.error(
                        f"{result.requirement.package} ({str(result.current_version)}) "
                        f"is {_time_delta.days} out of date. "
                        f"Latest version is: {result.latest_version}"
                    )
        else:
            logger.error(
                f"{result.requirement.package} ({str(result.current_version)}) is up to date"
            )

    if has_outdated_packages:
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
        "--calculate-rotten-between-releases",
        default=False,
        type=bool,
        help=(
            "Should calculate days out of date between releases? "
            "Defaults to False, meaning it will calculate delay "
            "between latest release date and today."
        ),
    )

    cli_parser.add_argument(
        "-d",
        "--delay",
        type=int,
        default=5,
        help=(
            "Delay before an outdated package triggers an error. "
            "(in days, defaults to 5)."
        ),
    )

    nargs = "+"

    if os.path.isfile("requirements.txt"):
        nargs = "*"
        default = ["requirements.txt"]

    cli_parser.add_argument(
        "files", nargs=nargs, type=str, default=default, help="requirements file(s)"
    )

    cli_args = cli_parser.parse_args()
    # call the main function to kick off the real work
    main(req_files=cli_args.files, delay=cli_args.delay)


if __name__ == "__main__":
    piprot()
