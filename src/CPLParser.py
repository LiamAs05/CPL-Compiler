# type: ignore

import random
from dataclasses import dataclass
from typing import Dict, List
from collections import Counter
from sly import Parser

from CPLLexer import CPLLexer


def is_number(s: str):
    return s.replace(".", "", 1).isdigit()


@dataclass
class IDList:
    l: List[str]


class Stack:
    def __init__(self):
        self._data = []

    def pop(self):
        return self._data.pop()

    def push(self, x):
        self._data.append(x)


class CPLParser(Parser):
    start = "program"
    tokens = CPLLexer.tokens

    def __init__(self):
        self._symtab: Dict[str, str] = {}
        self.code: str = ""
        self.label_counter = 0  # Increment after using
        self.label_stack = Stack()

    def relop_to_instruction(self, expr1, expr2, relop):
        prefix = self.symtab.get(expr1) or self.symtab.get(expr2)
        var = self.random_id_generator()
        code = {
            "==": f"{prefix}EQL {var} {expr1} {expr2}\n",
            "!=": f"{prefix}NQL {var} {expr1} {expr2}",
            "<": f"{prefix}LSS {var} {expr1} {expr2}",
            ">": f"{prefix}GRT {var} {expr1} {expr2}",
            ">=": f"{prefix}GRT {var} {expr1} {expr2}\n\
                JMPZ L{self.label_counter} {var}\n\
                {prefix}EQL {var} {expr1} {expr2}\n\
                L{self.label_counter}:",
            "<=": f"{prefix}LSS {var} {expr1} {expr2}\n\
                JMPZ L{self.label_counter} {var}\n\
                {prefix}EQL {var} {expr1} {expr2}\n\
                L{self.label_counter}:",
        }[relop]
        if relop in [">=", "<="]:
            self.label_counter += 1
        return code

    def determine_prefix(self, expr: str):
        freq = Counter(expr)
        if is_number(expr):
            return "I" if freq["."] == 0 else "R"
        return self.symtab.get(expr)

    def determine_expressions_prefix(self, expr1, expr2):
        if self.determine_prefix(expr1) == "R" or self.determine_prefix(expr2) == "R":
            return "R"
        return "I"

    @staticmethod
    def __gen(size):
        return "t" + "".join(random.choice("0123456789") for _ in range(size))

    def random_id_generator(self, type="I"):
        MAX_TRIES = 5
        GEN_SIZE = 1
        tries = 1
        res = CPLParser.__gen(1)

        while res in self.symtab:
            if tries < MAX_TRIES:
                tries += 1
            else:
                tries = 0
                GEN_SIZE += 1
            size = random.randint(1, GEN_SIZE)
            res = CPLParser.__gen(size)

        self.symtab[res] = type
        return res

    @_("declarations stmt_block")
    def program(self, p):
        return f"{self.code}HALT\n"

    # PART A - Declarations, DOES NOT GENERATE CODE

    @_("declarations declaration")
    def declarations(self, p):
        pass

    @_("")
    def declarations(self, p):
        pass

    @_("idlist COLON type SEMICOLON")
    def declaration(self, p):
        # Add vars to symbol table
        for _id in p.idlist.l:
            self.symtab[_id] = p.type

    @_("FLOAT")
    def type(self, p):
        return "R"

    @_("INT")
    def type(self, p):
        return "I"

    @_("idlist COMMA ID")
    def idlist(self, p):
        p.idlist.l.append(p.ID)
        return p.idlist

    @_("ID")
    def idlist(self, p):
        return IDList([p.ID])

    # END OF DECLARATIONS
    # PART B - Code!

    @_("assignment_stmt")
    def stmt(self, p):
        self.code += p.assignment_stmt

    @_("input_stmt")
    def stmt(self, p):
        self.code += p.input_stmt

    @_("output_stmt")
    def stmt(self, p):
        self.code += p.output_stmt

    @_("if_stmt")
    def stmt(self, p):
        self.code += p.if_stmt

    @_("while_stmt")
    def stmt(self, p):
        self.code += p.while_stmt

    @_("stmt_block")
    def stmt(self, p):
        self.code += p.stmt_block

    @_("ID ASSIGN expression SEMICOLON")
    def assignment_stmt(self, p):
        return f"{self.symtab[p.ID]}ASN {p.ID} {p.expression}\n"

    @_("INPUT LBRACE ID RBRACE SEMICOLON")
    def input_stmt(self, p):
        return f"{self.symtab[p.ID]}INP {p.ID}\n"

    @_("OUTPUT LBRACE expression RBRACE SEMICOLON")
    def output_stmt(self, p):
        return f"{self.symtab[p.expression]}PRT {p.expression}\n"

    @_("IF LBRACE boolexpr RBRACE stmt ELSE stmt")
    def if_stmt(self, p):
        pass

    @_("WHILE LBRACE boolexpr RBRACE stmt")
    def while_stmt(self, p):
        pass

    @_("LCBRACE stmtlist RCBRACE")
    def stmt_block(self, p):
        self.code += p.stmtlist or ""

    @_("stmtlist stmt")
    def stmtlist(self, p):
        self.code += p.stmtlist or ""
        self.code += p.stmt or ""

    @_("")
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
        return p.boolfactor

    @_("NOT LBRACE boolexpr RBRACE")
    def boolfactor(self, p):
        pass

    @_("expression RELOP expression")
    def boolfactor(self, p):
        return self.relop_to_instruction(p.expression0, p.expression1, p.RELOP)

    @_("expression ADDOP term")
    def expression(self, p):
        prefix = self.determine_expressions_prefix(p.expression, p.term)
        tmp = self.random_id_generator(prefix)
        instruction = "ADD" if p.ADDOP == "+" else "SUB"
        self.code += f"{prefix}{instruction} {tmp} {p.term} {p.expression}\n"
        return tmp

    @_("term")
    def expression(self, p):
        return p.term

    @_("term MULOP factor")
    def term(self, p):
        prefix = self.determine_expressions_prefix(p.term, p.factor)
        tmp = self.random_id_generator(prefix)
        instruction = "MLT" if p.MULOP == "*" else "DIV"
        self.code += f"{prefix}{instruction} {tmp} {p.term} {p.factor}\n"
        return tmp

    @_("factor")
    def term(self, p):
        return p.factor

    @_("LBRACE expression RBRACE")
    def factor(self, p):
        return p.expression

    @_("CAST LBRACE expression RBRACE")
    def factor(self, p):
        if "int" in p.CAST:
            self.symtab[p.expression] = "I"
            return f"RTOI {p.expression}\n"

        self.symtab[p.expression] = "R"
        return f"ITOR {p.expression}\n"

    @_("ID", "NUM")
    def factor(self, p):
        return p[0]

    def error(self, p):
        if not p:
            print("End of File!")
            return

        print(rf"An error was found in line {p.lineno}".upper())

        while True:
            tok = next(self.tokens, None)
            if not tok:
                break
        self.restart()

    @property
    def symtab(self) -> Dict[str, str]:
        return self._symtab

    @symtab.setter
    def symtab(self, symtab: Dict[str, str]) -> None:
        self._symtab = symtab
