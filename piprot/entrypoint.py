import argparse
import os
import sys

from piprot.piprot import Piprot


def entrypoint():
    cli_parser = argparse.ArgumentParser(
        epilog="Here's hoping your requirements are nice and fresh!"
    )

    cli_parser.add_argument(
        "-d",
        "--delay",
        type=int,
        default=5,
        help="Delay before an outdated package triggers an error. (in days, defaults to 5).",
    )

    if os.path.isfile("requirements.txt"):
        nargs = "*"
        default = ["requirements.txt"]
    else:
        nargs = "+"
        default = None

    cli_parser.add_argument(
        "files", nargs=nargs, type=str, default=default, help="requirements file(s)"
    )

    cli_args = cli_parser.parse_args()
    piprot = Piprot(req_files=cli_args.files, delay_in_days=cli_args.delay)
    sys.exit(piprot.main())


if __name__ == "__main__":
    entrypoint()
