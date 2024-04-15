from sys import stderr
from CPLCompiler import CPLCompiler


def main():
    sample = r"""a, b: float;
                {
                input(a);
                input(b);
                if (a < b)
                output(a); /* COMMENT */
                else
                output(b);
                }"""
    compiler = CPLCompiler(sample)
    compiler.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        stderr.write("Exiting...")
