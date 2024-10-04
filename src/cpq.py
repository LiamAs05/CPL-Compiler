import argparse
import sys
from typing import Tuple

from CPLCompiler import CPLCompiler


def main(data: str, outfile: str):
    compiler = CPLCompiler(data)
    compiler.run()
    print(compiler.program)

    with open(outfile, "w") as f:
        f.write(compiler.program)
        f.write("Signature Line - Liam Aslan, 215191347")


def get_args() -> Tuple[str, str]:
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
        sys.stderr.write("Signature Line - Liam Aslan, 215191347\n")
        main(*get_args())
    except KeyboardInterrupt:
        sys.stderr.write("Exiting...")
