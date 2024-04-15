from CPLLexer import CPLLexer
from CPLParser import CPLParser


class CPLCompiler:
    def __init__(self, program: str):
        self.lexer: CPLLexer = CPLLexer()
        self.parser: CPLParser = CPLParser()
        self.symtab: dict[str, str] = {}
        self.program: str = program
        self.tokens: list = None

    def __run_lexer(self):
        self.tokens = self.lexer.tokenize(self.program)
        token = next(self.tokens)

        try:
            while True:
                if token.type == "ID":
                    self.symtab[token.value] = token.type
                token = next(self.tokens)
        except StopIteration:
            pass  # End of tokens

    def __run_parser(self):
        self.parser.parse(self.tokens)

    def run(self):
        self.__run_lexer()
        self.__run_parser()
