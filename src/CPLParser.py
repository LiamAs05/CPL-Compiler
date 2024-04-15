from sly import Parser
from CPLLexer import CPLLexer


class CPLParser(Parser):
    # Get the token list from the lexer (required)
    tokens = CPLLexer.tokens

    # Grammar rules and actions
    @_("declarations stmt_block")
    def program(self, p):
        pass

    @_("declarations declaration")
    def declarations(self, p):
        pass

    @_("idlist COLON type SEMICOLON")
    def declaration(self, p):
        pass

    @_("FLOAT")
    def type(self, p):
        pass

    @_("INT")
    def type(self, p):
        pass

    @_("idlist COMMA ID")
    def idlist(self, p):
        pass

    @_("ID")
    def idlist(self, p):
        pass

    @_("assignment_stmt")
    def stmt(self, p):
        pass

    @_("input_stmt")
    def stmt(self, p):
        pass

    @_("output_stmt")
    def stmt(self, p):
        pass

    @_("if_stmt")
    def stmt(self, p):
        pass

    @_("while_stmt")
    def stmt(self, p):
        pass

    @_("stmt_block")
    def stmt(self, p):
        pass

    @_("ID ASSIGN expression SEMICOLON")
    def assignment_stmt(self, p):
        pass

    @_("INPUT LBRACE ID RBRACE SEMICOLON")
    def input_stmt(self, p):
        pass

    @_("OUTPUT LBRACE expression RBRACE SEMICOLON")
    def output_stmt(self, p):
        pass

    @_("IF LBRACE boolexpr RBRACE stmt ELSE stmt")
    def if_stmt(self, p):
        pass

    @_("WHILE LBRACE boolexpr RBRACE stmt")
    def while_stmt(self, p):
        pass

    @_("LCBRACE stmtlist RCBRACE")
    def stmt_block(self, p):
        pass

    @_("stmtlist stmt")
    def stmtlist(self, p):
        pass

    @_("boolexpr OR boolterm")
    def boolexpr(self, p):
        pass

    @_("boolterm")
    def boolexpr(self, p):
        pass

    @_("boolterm AND boolfactor")
    def boolterm(self, p):
        pass

    @_("boolfactor")
    def boolterm(self, p):
        pass

    @_("NOT LBRACE boolexpr RBRACE")
    def boolfactor(self, p):
        pass

    @_("expression RELOP expression")
    def boolfactor(self, p):
        pass

    @_("expression ADDOP term")
    def expression(self, p):
        pass

    @_("term")
    def expression(self, p):
        pass

    @_("term MULOP factor")
    def term(self, p):
        pass

    @_("factor")
    def term(self, p):
        pass

    @_("LBRACE expression RBRACE")
    def factor(self, p):
        pass

    @_("CAST LBRACE expression RBRACE")
    def factor(self, p):
        pass

    @_("ID")
    def factor(self, p):
        pass

    @_("NUM")
    def factor(self, p):
        pass

    # def error(self, p):
    #     print(rf"An error was found in line {p.lineno}".upper())
    #     if not p:
    #         print("End of File!")
    #         return

    #     while True:
    #         tok = next(self.tokens, None)
    #         if not tok:
    #             break
    #     self.restart()
