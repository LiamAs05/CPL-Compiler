# type: ignore

import sys
from collections import Counter
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from sly import Parser

from CPLLexer import CPLLexer

ERR = -1


def is_number(s: str):
    return s.replace(".", "", 1).isdigit()


@dataclass
class IDList:
    l: List[str]


@dataclass
class QuadResult:
    code: str
    value: str


@dataclass
class Queue:
    _data: list[str]

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
        self.label_counter = 0  # Increment after using
        self.var_counter = 0
        self.error_queue = Queue([])

    def generate_while_stmt(self, boolexpr, boolexpr_res, stmt) -> QuadResult:
        start_label = self.generate_label()
        end_label = self.generate_label()
        code_to_add = f"JUMP {end_label}\n"
        code_to_add += f"{start_label}:\n"
        code_to_add += stmt
        code_to_add += f"{end_label}:\n"
        code_to_add += boolexpr
        code_to_add += f"ISUB {boolexpr_res} {1} {boolexpr_res}\n"
        code_to_add += f"JMPZ {start_label} {boolexpr_res}\n"
        return QuadResult(code_to_add, "")

    def generate_if_stmt(self, boolexpr, boolexpr_res, stmt1, stmt2) -> QuadResult:
        else_label = self.generate_label()
        both_label = self.generate_label()

        code_to_add = boolexpr
        code_to_add += f"JMPZ {else_label} {boolexpr_res}\n"
        code_to_add += stmt1
        code_to_add += f"JUMP {both_label}\n"
        code_to_add += f"{else_label}:\n"
        code_to_add += stmt2
        code_to_add += f"{both_label}:\n"
        return QuadResult(code_to_add, "")

    def relop_to_instruction(self, expr1, expr2, relop) -> QuadResult:
        """
        Translates RELOP tokens into QUAD instructions.
        For operators which are not ">=" and "<=" the translation is trivial.
        For ">=" and "<=" we check both conditions and perform an OR between them.
        """
        code = ""
        prefix, index, cast_var = self.determine_prefix_noerror(expr1, expr2)
        if cast_var.value:
            if index == 1:
                expr1 = cast_var.value
            else:
                expr2 = cast_var.value
        condition_result = self.generate_tmp_id()
        translator = lambda var, type: {
            "==": f"{prefix}EQL {var} {expr1} {expr2}\n",
            "!=": f"{prefix}NQL {var} {expr1} {expr2}\n",
            "<": f"{prefix}LSS {var} {expr1} {expr2}\n",
            ">": f"{prefix}GRT {var} {expr1} {expr2}\n",
        }[type]

        if relop in [">=", "<="]:
            second_condition_result = self.generate_tmp_id()
            code += translator(condition_result, "==")
            code += translator(second_condition_result, relop[0])
            condition_result = self.generate_or(
                condition_result, second_condition_result
            )
        else:
            code += translator(condition_result, relop)
        return QuadResult(cast_var.code + code, condition_result)

    def generate_or(self, boolexpr, boolterm) -> QuadResult:
        tmp = self.generate_tmp_id()
        code = f"IADD {tmp} {boolexpr} {boolterm}\n"
        code += f"IGRT {tmp} {tmp} {0}\n"
        return QuadResult(code, tmp)

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

    def determine_prefix_noerror(self, expr1, expr2) -> Tuple[str, int, QuadResult]:
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
            -   cast result -- value and code

            if a cast was performed the second and third return values indicate which variable to replace with the cast result.
            if a cast wasn't performed they are 0 and None.
        """
        expr1_prefix = self.determine_prefix(expr1)
        expr2_prefix = self.determine_prefix(expr2)

        if expr1_prefix == expr2_prefix:
            return expr1_prefix, 0, QuadResult("", "")

        if expr1_prefix == "I":
            return "R", 1, self.cast("R", expr1)

        return "R", 2, self.cast("R", expr2)

    def generate_mulop(self, mulop, term, factor) -> QuadResult:
        prefix, which_cast, cast_var = self.determine_prefix_noerror(
            term,
            factor,
        )
        if cast_var.value:
            if which_cast == 1:
                term = cast_var.value
            else:
                factor = cast_var.value

        tmp = self.generate_tmp_id(prefix)
        instruction = "MLT" if mulop == "*" else "DIV"
        code = f"{prefix}{instruction} {tmp} {term} {factor}\n"
        return QuadResult(cast_var.code + code, tmp)

    def generate_addop(self, addop, expr, term):
        prefix, which_cast, cast_var = self.determine_prefix_noerror(
            expr,
            term,
        )
        if cast_var.value:
            if which_cast == 1:
                expr = cast_var.value
            else:
                term = cast_var.value

        tmp = self.generate_tmp_id(prefix)
        instruction = "ADD" if addop == "+" else "SUB"
        code = f"{prefix}{instruction} {tmp} {expr} {term}\n"
        return QuadResult(cast_var.code + code, tmp)

    def __gen(self):
        self.var_counter += 1
        return f"t{self.var_counter}"

    def __gen_label(self):
        self.label_counter += 1
        return f"L{self.label_counter}"

    def generate_tmp_id(self, type="I"):
        res = self.__gen()

        while res in self.symtab:
            res = CPLParser.__gen()

        self.symtab[res] = type
        return res

    def generate_label(self):
        return self.__gen_label()

    def cast(self, to, expr) -> QuadResult:
        tmp = self.generate_tmp_id(to)
        _from = "R" if to == "I" else "I"
        return QuadResult(f"{_from}TO{to} {tmp} {expr}\n", tmp)

    @_("declarations stmt_block")
    def program(self, p) -> Optional[str]:
        """
        Main grammer rule, will return the full quad program unless an error occured.

        Returns:
            Optional[str]
        """
        if not self.error_queue.empty():
            self.error_queue.print()
            return None

        code = p.stmt_block.code or ""
        return f"{code}HALT\n"

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
        return QuadResult(p.assignment_stmt.code, "")

    @_("input_stmt")
    def stmt(self, p):
        return QuadResult(p.input_stmt.code, "")

    @_("output_stmt")
    def stmt(self, p):
        return QuadResult(p.output_stmt.code, "")

    @_("if_stmt")
    def stmt(self, p):
        return QuadResult(p.if_stmt.code, "")

    @_("while_stmt")
    def stmt(self, p):
        return QuadResult(p.while_stmt.code, "")

    @_("stmt_block")
    def stmt(self, p):
        return QuadResult(p.stmt_block.code or "", "")

    @_("ID ASSIGN expression SEMICOLON")
    def assignment_stmt(self, p) -> QuadResult:
        if self.determine_expressions_prefix(p.lineno, p.ID, p.expression.value) == ERR:
            return QuadResult("", "")
        code = f"{self.symtab[p.ID]}ASN {p.ID} {p.expression.value}\n"
        return QuadResult(p.expression.code + code, "")

    @_("INPUT LBRACE ID RBRACE SEMICOLON")
    def input_stmt(self, p) -> QuadResult:
        code = f"{self.symtab[p.ID]}INP {p.ID}\n"
        return QuadResult(code, "")

    @_("OUTPUT LBRACE expression RBRACE SEMICOLON")
    def output_stmt(self, p) -> QuadResult:
        code = f"{self.symtab[p.expression.value]}PRT {p.expression.value}\n"
        return QuadResult(p.expression.code + code, "")

    @_("IF LBRACE boolexpr RBRACE stmt ELSE stmt")
    def if_stmt(self, p):
        return self.generate_if_stmt(
            p.boolexpr.code, p.boolexpr.value, p.stmt0.code, p.stmt1.code
        )

    @_("WHILE LBRACE boolexpr RBRACE stmt")
    def while_stmt(self, p) -> QuadResult:
        return self.generate_while_stmt(p.boolexpr.code, p.boolexpr.value, p.stmt.code)

    @_("LCBRACE stmtlist RCBRACE")
    def stmt_block(self, p) -> QuadResult:
        return QuadResult(p.stmtlist.code or "", "")

    @_("stmtlist stmt")
    def stmtlist(self, p) -> QuadResult:
        return QuadResult(p.stmtlist.code + p.stmt.code, "")

    @_("")
    def stmtlist(self, p) -> QuadResult:
        return QuadResult("", "")

    @_("boolexpr OR boolterm")
    def boolexpr(self, p) -> QuadResult:
        return self.generate_or(p.boolexpr.value, p.boolterm.value)

    @_("boolterm")
    def boolexpr(self, p):
        return QuadResult(p.boolterm.code, p.boolterm.value)

    @_("boolterm AND boolfactor")
    def boolterm(self, p) -> QuadResult:
        tmp = self.generate_tmp_id()
        code = f"IMLT {tmp} {p.boolterm.value} {p.boolfactor.value}\n"
        return QuadResult(code, tmp)

    @_("boolfactor")
    def boolterm(self, p) -> QuadResult:
        return QuadResult(p.boolfactor.code, p.boolfactor.value)

    @_("NOT LBRACE boolexpr RBRACE")
    def boolfactor(self, p) -> QuadResult:
        tmp = self.generate_tmp_id()
        code = f"ISUB {tmp} {1} {p.boolexpr.value}\n"
        return QuadResult(code, tmp)

    @_("expression RELOP expression")
    def boolfactor(self, p) -> QuadResult:
        return self.relop_to_instruction(
            p.expression0.value, p.expression1.value, p.RELOP
        )

    @_("expression ADDOP term")
    def expression(self, p) -> QuadResult:
        res = self.generate_addop(p.ADDOP, p.expression.value, p.term.value)
        return QuadResult(p.expression.code + p.term.code + res.code, res.value)

    @_("term")
    def expression(self, p) -> QuadResult:
        return p.term

    @_("term MULOP factor")
    def term(self, p) -> QuadResult:
        res = self.generate_mulop(p.MULOP, p.term.value, p.factor.value)
        return QuadResult(p.term.code + p.factor.code + res.code, res.value)

    @_("factor")
    def term(self, p) -> QuadResult:
        return p.factor

    @_("LBRACE expression RBRACE")
    def factor(self, p) -> QuadResult:
        return p.expression

    @_("CAST LBRACE expression RBRACE")
    def factor(self, p) -> QuadResult:
        if "int" in p.CAST:
            return self.cast("I", p.expression.value)
        return self.cast("R", p.expression.value)

    @_("ID", "NUM")
    def factor(self, p) -> QuadResult:
        return QuadResult("", p[0])

    def error(self, p):
        """
        Documents actual parsing errors (and not schematic errors, such as mismatched types)

        Examples include:

        -   A program without {}
        -   not assigning the result of a cast
        """
        if not p:
            sys.stderr.write(
                "ERROR: The tokenized program does not match the grammer of a valid CPL program.\n"
            )
            return

        sys.stderr.write(f"An error was found in line {p.lineno}\n")

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
