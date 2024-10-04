# type: ignore

import random
import string
from dataclasses import dataclass
from typing import Dict, List

from sly import Parser

from CPLLexer import CPLLexer


@dataclass
class IDList:
    l: List[str]


class CPLParser(Parser):
    start = "program"
    tokens = CPLLexer.tokens

    def __init__(self):
        self._symtab: Dict[str, str] = {}
        self.label_counter = 0  # Increment after using

    def relop_to_instruction(self, expr1, expr2, relop):
        prefix = self.symtab[expr1]
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

    @staticmethod
    def __gen(size):
        return "".join(random.choice(string.ascii_lowercase) for _ in range(size))

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
        return p.stmt_block + "HALT\n"

    # PART A - Declarations, DOES NOT GENERATE CODE

    @_("declarations declaration")
    def declarations(self, p):
        pass

    @_("")
    def declarations(self, p):
        pass

    @_("idlist COLON type SEMICOLON")
    def declaration(self, p):
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

    # PART B - Code! Assume symbol table is built :)

    @_("assignment_stmt")
    def stmt(self, p):
        return p.assignment_stmt

    @_("input_stmt")
    def stmt(self, p):
        return p.input_stmt

    @_("output_stmt")
    def stmt(self, p):
        return p.output_stmt

    @_("if_stmt")
    def stmt(self, p):
        return p.if_stmt

    @_("while_stmt")
    def stmt(self, p):
        return p.while_stmt

    @_("stmt_block")
    def stmt(self, p):
        return p.stmt_block

    @_("ID ASSIGN expression SEMICOLON")
    def assignment_stmt(self, p):
        return f"{self.symtab[p.ID]}ASN {p.ID} {p.expression}\n"

    @_("INPUT LBRACE ID RBRACE SEMICOLON")
    def input_stmt(self, p):
        return f"{self.symtab[p.ID]}INP {p.ID}\n"

    @_("OUTPUT LBRACE expression RBRACE SEMICOLON")
    def output_stmt(self, p):
        return f"IPRT {p.expression}\n"

    @_("IF LBRACE boolexpr RBRACE stmt ELSE stmt")
    def if_stmt(self, p):
        pass

    @_("WHILE LBRACE boolexpr RBRACE stmt")
    def while_stmt(self, p):
        pass

    @_("LCBRACE stmtlist RCBRACE")
    def stmt_block(self, p):
        stmtlist = f"{p.stmtlist}\n" if p.stmtlist else ""
        return f"{stmtlist}L{self.label_counter}:\n"

    @_("stmtlist stmt")
    def stmtlist(self, p):
        return p.stmtlist + p.stmt

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
        prefix = self.symtab[p.factor]
        if p.ADDOP == "+":
            return (
                f"{prefix}ADD {self.random_id_generator(prefix)} {p.term} {p.factor}\n"
            )
        elif p.ADDOP == "-":
            return (
                f"{prefix}SUB {self.random_id_generator(prefix)} {p.term} {p.factor}\n"
            )

    @_("term")
    def expression(self, p):
        return p.term

    @_("term MULOP factor")
    def term(self, p):
        prefix = self.symtab[p.factor]
        if p.MULOP == "*":
            return (
                f"{prefix}MLT {self.random_id_generator(prefix)} {p.term} {p.factor}\n"
            )
        elif p.MULOP == "/":
            return (
                f"{prefix}DIV {self.random_id_generator(prefix)} {p.term} {p.factor}\n"
            )

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
