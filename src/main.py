from sys import stderr
from CPLCompiler import CPLCompiler


def main():
    sample = r"""a, b: float;
                {
                input(a);
                input(b);
                if (a < b)
                output(a);
                else
                output(b);
                }"""
    compiler = CPLCompiler()
    compiler.run_lexer(sample)
    print(compiler.symtab)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        stderr.write("Exiting...")
