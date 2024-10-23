# type: ignore

from sly import Lexer


class CPLLexer(Lexer):
    tokens = {
        ELSE,
        FLOAT,
        IF,
        INPUT,
        INT,
        OUTPUT,
        WHILE,
        LBRACE,
        RBRACE,
        LCBRACE,
        RCBRACE,
        COMMA,
        COLON,
        SEMICOLON,
        ASSIGN,
        NUM,
        ID,
        RELOP,
        ADDOP,
        MULOP,
        OR,
        AND,
        NOT,
        CAST,
    }

    # String containing ignored characters
    ignore = r" \t"
    ignore_comment = r"\/\*[^*]*\*+([^\/*][^*]*\*+)*\/"

    # Regular expression rules for tokens
    ELSE = r"else"
    FLOAT = r"float"
    IF = r"if"
    INPUT = r"input"
    INT = r"int"
    OUTPUT = r"output"
    WHILE = r"while"
    LCBRACE = r"\{"
    RCBRACE = r"\}"
    LBRACE = r"\("
    RBRACE = r"\)"
    COMMA = r","
    COLON = r":"
    SEMICOLON = r";"
    RELOP = r"(>=|<=|==|!=|<|>)"
    ASSIGN = r"="
    NUM = r"[0-9]+\.[0-9]*|[0-9]+"
    CAST = r"(static_cast<int>)|(static_cast<float>)"
    ID = r"[a-zA-Z]([a-zA-Z]|[0-9])*"
    ADDOP = r"[+-]"
    MULOP = r"[*/]"
    OR = r"\|\|"
    AND = r"&&"
    NOT = r"!"

    # Line number tracking
    @_(r"\s+")
    def ignore_newline(self, t):
        self.lineno += t.value.count("\n")

    def error(self, t):
        print(rf"Line {self.lineno}: Bad character {t.value[0]}")
        self.index += 1
