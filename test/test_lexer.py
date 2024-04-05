import pytest
from src.CPLLexer import CPLLexer


@pytest.fixture
def lexer():
    return CPLLexer()


def test_tokens(lexer):
    # Test token recognition
    tokens = [
        ("break", "BREAK"),
        ("case", "CASE"),
        ("default", "DEFAULT"),
        ("else", "ELSE"),
        ("float", "FLOAT"),
        ("if", "IF"),
        ("input", "INPUT"),
        ("int", "INT"),
        ("output", "OUTPUT"),
        ("switch", "SWITCH"),
        ("while", "WHILE"),
        ("{", "LCBRACE"),
        ("}", "RCBRACE"),
        ("(", "LBRACE"),
        (")", "RBRACE"),
        (",", "COMMA"),
        (":", "COLON"),
        (";", "SEMICOLON"),
        ("=", "ASSIGN"),
        ("123", "NUM"),
        ("identifier", "ID"),
        ("==", "RELOP"),
        ("+", "ADDOP"),
        ("*", "MULOP"),
        ("||", "OR"),
        ("&&", "AND"),
        ("!", "NOT"),
        ("static_cast<int>", "CAST"),
        ("/* Comment */", "COMMENT"),
    ]

    for input_text, expected_token in tokens:
        lex = lexer.tokenize(input_text)
        token = next(lex)
        assert token.type == expected_token


def test_ignore_newline(lexer):
    # Test newline ignoring
    input_text = "\n\n\nBye"
    lex = lexer.tokenize(input_text)
    token = next(lex)
    assert token.type == "ID"
    assert lexer.lineno == 4  # Start from 1, go down 3 lines


def test_sample_program(lexer):
    sample = r"""a, b: float;
                {
                input(a);
                input(b);
                if (a < b)
                output(a);
                else
                output(b);
                }"""
    lex = lexer.tokenize(sample)
    l = list(map(lambda x: x.value, lex))

    assert l == [
        "a",
        ",",
        "b",
        ":",
        "float",
        ";",
        "{",
        "input",
        "(",
        "a",
        ")",
        ";",
        "input",
        "(",
        "b",
        ")",
        ";",
        "if",
        "(",
        "a",
        "<",
        "b",
        ")",
        "output",
        "(",
        "a",
        ")",
        ";",
        "else",
        "output",
        "(",
        "b",
        ")",
        ";",
        "}",
    ]

    lex = lexer.tokenize(sample)
    l = list(map(lambda x: x.type, lex))
    assert l == [
        "ID",
        "COMMA",
        "ID",
        "COLON",
        "FLOAT",
        "SEMICOLON",
        "LCBRACE",
        "INPUT",
        "LBRACE",
        "ID",
        "RBRACE",
        "SEMICOLON",
        "INPUT",
        "LBRACE",
        "ID",
        "RBRACE",
        "SEMICOLON",
        "IF",
        "LBRACE",
        "ID",
        "RELOP",
        "ID",
        "RBRACE",
        "OUTPUT",
        "LBRACE",
        "ID",
        "RBRACE",
        "SEMICOLON",
        "ELSE",
        "OUTPUT",
        "LBRACE",
        "ID",
        "RBRACE",
        "SEMICOLON",
        "RCBRACE",
    ]
