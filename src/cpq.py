import argparse
import sys
from typing import Tuple

from CPLCompiler import CPLCompiler


def main(data: str, outfile: str):
    sys.stderr.write("Signature Line - Liam Aslan, 215191347\n")

    with CPLCompiler(data, outfile) as compiler:
        print(compiler.program)


def get_args() -> Tuple[str, str]:
    """
    Internal functions to handle arguments

    Raises:
        KeyError: In case filenames does not end with `.ou`

    Returns:
        Tuple[str, str]: file contents and file name
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="CPL program file")
    filename = parser.parse_args().input

    if not filename.endswith(".ou"):
        raise KeyError('Invalid Filename: Filenames must end with ".ou" extension')

    with open(filename, "r") as f:
        data = f.read()

    filename = filename.split(".")[0]
    return data, filename + ".qud"


if __name__ == "__main__":
    try:
        main(*get_args())
    except KeyboardInterrupt:
        sys.stderr.write("Exiting...")
    except Exception as e:
        sys.stderr.write(f"An unhandled exception has occurred.\n{e.with_traceback()}")
