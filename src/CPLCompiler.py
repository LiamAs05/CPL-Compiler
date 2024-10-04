from typing import List

from CPLLexer import CPLLexer
from CPLParser import CPLParser


class CPLCompiler:
    def __init__(self, input_cpl_program: str):
        self._lexer: CPLLexer = CPLLexer()
        self._parser: CPLParser = CPLParser()
        self._cpl_program: str = input_cpl_program
        self._output_program: str = ""
        self._tokens: List = None

    def run(self):
        self._tokens = self._lexer.tokenize(self._cpl_program)
        self._output_program = self._parser.parse(self._tokens)

    @property
    def program(self):
        return self._output_program
