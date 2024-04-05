from CPLLexer import CPLLexer
from CPLParser import CPLParser


class CPLCompiler:
    def __init__(self):
        self.lexer: CPLLexer = CPLLexer()
        # self.parser: CPLParser = CPLParser()
        self.symtab: dict[str, str] = {}

    def run_lexer(self, program: str):
        lex = self.lexer.tokenize(program)
        token = next(lex)

        try:
            while True:
                if token.type == "ID":
                    self.symtab[token.value] = token.type
                token = next(lex)
        except StopIteration:
            pass  # End of tokens
