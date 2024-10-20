import sys
from typing import List

from CPLLexer import CPLLexer
from CPLParser import CPLParser


class CPLCompiler:
    def __init__(self, input_cpl_program: str, output_filename: str):
        self._lexer: CPLLexer = CPLLexer()
        self._parser: CPLParser = CPLParser()
        self._cpl_program: str = input_cpl_program
        self._output_filename: str = output_filename
        self._output_program: str = ""
        self._tokens: List = None

    def __enter__(self):
        self.run()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            sys.stderr.write(
                f"An exception occurred while compiling {self._output_filename}.\n\
                See stderr for possible parse and lexical errors."
            )
            return

        with open(self._output_filename, "w") as f:
            f.write(self.program)
            f.write("Signature Line - Liam Aslan, 215191347")

    def run(self):
        self._tokens = self._lexer.tokenize(self._cpl_program)
        self._output_program = self._parser.parse(self._tokens)

    @property
    def program(self):
        return self._output_program
