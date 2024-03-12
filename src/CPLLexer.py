from sly import Lexer


class CPLLexer(Lexer):
    tokens = {
        ERROR,
        BREAK,
        CASE,
        DEFAULT,
        ELSE,
        FLOAT,
        IF,
        INPUT,
        INT,
        OUTPUT,
        SWITCH,
        WHILE,
        LEFT_BRACE,
        RIGHT_BRACE,
        LEFT_CURLY_BRACE,
        RIGHT_CURLY_BRACE,
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
        COMMENT,
    }

    # String containing ignored characters
    ignore = r" "

    # Regular expression rules for tokens
    BREAK = r"break"
    CASE = r"case"
    DEFAULT = r"default"
    ELSE = r"else"
    FLOAT = r"float"
    IF = r"if"
    INPUT = r"input"
    INT = r"int"
    OUTPUT = r"output"
    SWITCH = r"switch"
    WHILE = r"while"
    LEFT_CURLY_BRACE = r"\{"
    RIGHT_CURLY_BRACE = r"\}"
    LEFT_BRACE = r"\("
    RIGHT_BRACE = r"\)"
    COMMA = r","
    COLON = r":"
    SEMICOLON = r";"
    RELOP = r"(==|!=|<|>|>=|<=)"
    ASSIGN = r"="
    NUM = r"[0-9]+\.[0-9]*|[0-9]+"
    CAST = r"(static_cast<int>)|(static_cast<float>)"
    ID = r"[a-zA-Z]([a-zA-Z]|[0-9])*"
    ADDOP = r"[+-]"
    COMMENT = r"\/\*[^*]*\*+([^\/*][^*]*\*+)*\/"
    MULOP = r"[*/]"
    OR = r"\|\|"
    AND = r"&&"
    NOT = r"!"

    # Line number tracking
    @_(r"\n+")
    def ignore_newline(self, t):
        self.lineno += t.value.count("\n")

    def error(self, t):
        print(rf"Line {self.lineno}: Bad character {t.value[0]}")
        self.index += 1
