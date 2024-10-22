import argparse
import sys
from typing import Optional, Tuple


def get_args() -> Tuple[str, str]:
    """
    Internal functions to handle arguments

    Checks for the following errors:
    -   Filename was not provided
    -   Filename does not end with `.ou`
    -   Filename is not a valid path

    Shows an error message according to each case and exits with code 0.

    Returns:
        Tuple[str, str]: file contents and output file name
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input", nargs="?", type=str, help="CPL program file", default=None
    )

    filename = parser.parse_args().input

    check_file_validity(filename, parser.prog)

    return attempt_to_read_file(filename), filename.replace(".ou", ".qud")


def check_file_validity(filename: str, prog: str) -> None:
    """
    Checks if the input file exists and has the correct extension.

    Args:
        filename (str)
        prog (str): program name, for error messages
    """
    if not filename:
        sys.stderr.write(
            f"ERROR (No Input File): An input file must be provided.\n\
Usage: {prog} <filename.ou>"
        )
        sys.exit(0)

    if not filename.endswith(".ou"):
        sys.stderr.write(
            'ERROR (Invalid Filename): Filenames must end with ".ou" extension.'
        )
        sys.exit(0)


def attempt_to_read_file(filename: str) -> Optional[str]:
    """
    Tries to open and read a file, prints an error message if the file does not exist.
    Exits with 0 if the file could not be read.

    Args:
        filename (str)

    Returns:
        Optional[str]: returns the content of the file if the read was successful.
    """
    try:
        with open(filename, "r") as f:
            return f.read()
    except IOError:
        sys.stderr.write(
            f"ERROR (Input File Does Not Exist): {filename} is not a valid path."
        )
        sys.exit(0)
