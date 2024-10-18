# type: ignore

from collections import Counter
from dataclasses import dataclass
from typing import Dict, List, Tuple

from sly import Parser

from CPLLexer import CPLLexer

ERR = -1


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


class Queue:
    def __init__(self):
        self._data = []

    def pop(self):
        return self._data.pop(0)

    def push(self, x):
        self._data.append(x)

    def empty(self):
        return len(self._data) == 0

    def print(self):
        while not self.empty():
            print(self.pop())


class CPLParser(Parser):
    start = "program"
    tokens = CPLLexer.tokens

    def __init__(self):
        self._symtab: Dict[str, str] = {}
        self.code: str = ""
        self.label_counter = 0  # Increment after using
        self.var_counter = 0
        self.label_stack = Stack()
        self.error_queue = Queue()

    def relop_to_instruction(self, expr1, expr2, relop):
        prefix = self.symtab.get(expr1) or self.symtab.get(expr2)
        var = self.generate_tmp_id()
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

    def determine_prefix(self, expr: str) -> str:
        """
        Internal function which determines the type of a single expression

        examples:
        self.determine_prefix(5) -> "I"
        self.determine_prefix(5.0) -> "R"
        self.determine_prefix(t1) -> SymbolTable[t1]

        Args:
            expr (str): _description_

        Returns:
            str: _description_
        """
        freq = Counter(expr)
        if is_number(expr):
            return "I" if freq["."] == 0 else "R"
        return self.symtab.get(expr)

    def determine_expressions_prefix(self, lineno, expr1, expr2):
        """
        Determines the prefix of an instruction with two operands.
        If an error occurs, returns ERR code and pushes to error queue.

        Args:
            lineno (int)
            expr1 (str): first operand
            expr2 (str): second operand

        Returns:
            str: prefix
        """
        if self.determine_prefix(expr1) != self.determine_prefix(expr2):
            self.error_queue.push(
                f"ERROR in line {lineno}: Operands must be of same type."
            )
            return ERR

        if self.determine_prefix(expr1) == "R":
            return "R"
        return "I"

    def determine_prefix_noerror(self, expr1, expr2) -> Tuple[str, int, str]:
        """
        For use with functions that require implicit casting,
        for example addition and multiplication, where two mismatched operands don't result in an error.

        Args:
            expr1 (str): first operand
            expr2 (str): second operand

        Returns:
            Tuple[str, int, str]:

            -   instruction prefix
            -   cast operand index
            -   cast result

            if a cast was performed the second and third return values indicate which variable to replace with the cast result.
            if a cast wasn't performed they are 0 and None.
        """
        expr1_prefix = self.determine_prefix(expr1)
        expr2_prefix = self.determine_prefix(expr2)

        if expr1_prefix == expr2_prefix:
            return expr1_prefix, 0, None

        if expr1_prefix == "I":
            return "R", 1, self.cast("R", expr1)

        return "R", 2, self.cast("R", expr2)

    def __gen(self):
        self.var_counter += 1
        return f"t{self.var_counter}"

    def generate_tmp_id(self, type="I"):
        res = self.__gen()

        while res in self.symtab:
            res = CPLParser.__gen()

        self.symtab[res] = type
        return res

    def cast(self, to, expr):
        tmp = self.generate_tmp_id(to)
        _from = "R" if to == "I" else "I"
        self.code += f"{_from}TO{to} {tmp} {expr}\n"
        return tmp

    @_("declarations stmt_block")
    def program(self, p):
        self.error_queue.print()
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
        if self.determine_expressions_prefix(p.lineno, p.ID, p.expression) == ERR:
            self.code = ""
            return ""
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
        expression = p.expression
        term = p.term
        prefix, which_cast, cast_var = self.determine_prefix_noerror(
            p.expression, p.term
        )
        if cast_var:
            if which_cast == 1:
                expression = cast_var
            else:
                term = cast_var

        tmp = self.generate_tmp_id(prefix)
        instruction = "ADD" if p.ADDOP == "+" else "SUB"
        self.code += f"{prefix}{instruction} {tmp} {expression} {term}\n"
        return tmp

    @_("term")
    def expression(self, p):
        return p.term

    @_("term MULOP factor")
    def term(self, p):
        term = p.term
        factor = p.factor
        prefix, which_cast, cast_var = self.determine_prefix_noerror(p.term, p.factor)
        if cast_var:
            if which_cast == 1:
                term = cast_var
            else:
                factor = cast_var

        tmp = self.generate_tmp_id(prefix)
        instruction = "MLT" if p.MULOP == "*" else "DIV"
        self.code += f"{prefix}{instruction} {tmp} {term} {factor}\n"
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
            return self.cast("I", p.expression)
        else:
            return self.cast("R", p.expression)

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
