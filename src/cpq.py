import sys

import FileHelper
from CPLCompiler import CPLCompiler


def main(data: str, outfile: str):
    sys.stderr.write("Signature Line - Liam Aslan, 215191347\n")

    with CPLCompiler(data, outfile) as compiler:
        print(compiler.program or "", end="")


if __name__ == "__main__":
    try:
        main(*FileHelper.get_args())
    except KeyboardInterrupt:
        sys.stderr.write("CTRL+C Pressed, exiting...")
    except Exception as e:
        sys.stderr.write(f"An unhandled exception occurred.\n{e}")
