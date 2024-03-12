
class TreeParser(Parser):
    # Get the token list from the lexer (required)
    tokens = TreeLexer.tokens

    # Grammar rules and actions
    @_("tree")
    def S(self, p):
        return p.tree.val

    @_("LBRACE SUM treelist RBRACE")
    def tree(self, p):
        return Tree(p.treelist.sum, p.treelist.height + 1)

    @_("LBRACE ZERO treelist RBRACE")
    def tree(self, p):
        return Tree(0, p.treelist.height + 1)

    @_("LBRACE HEIGHT treelist RBRACE")
    def tree(self, p):
        return Tree(p.treelist.height + 1, p.treelist.height + 1)

    @_("LBRACE DOUBLE tree RBRACE")
    def tree(self, p):
        return Tree(p.tree.val * 2, p.tree.height + 1)

    @_("NUMBER")
    def tree(self, p):
        return Tree(int(p.NUMBER), 0)

    @_("treelist tree")
    def treelist(self, p):
        return Treelist(
            p.treelist.sum + p.tree.val, max(p.treelist.height, p.tree.height)
        )

    @_("tree")
    def treelist(self, p):
        return Treelist(p.tree.val, p.tree.height)

    def error(self, p):
        print(rf"An error was found in line {p.lineno}".upper())
        if not p:
            print("End of File!")
            return

        while True:
            tok = next(self.tokens, None)
            if not tok:
                break
        self.restart()
class TreeParser(Parser):
    # Get the token list from the lexer (required)
    tokens = TreeLexer.tokens

    # Grammar rules and actions
    @_("tree")
    def S(self, p):
        return p.tree.val

    @_("LBRACE SUM treelist RBRACE")
    def tree(self, p):
        return Tree(p.treelist.sum, p.treelist.height + 1)

    @_("LBRACE ZERO treelist RBRACE")
    def tree(self, p):
        return Tree(0, p.treelist.height + 1)

    @_("LBRACE HEIGHT treelist RBRACE")
    def tree(self, p):
        return Tree(p.treelist.height + 1, p.treelist.height + 1)

    @_("LBRACE DOUBLE tree RBRACE")
    def tree(self, p):
        return Tree(p.tree.val * 2, p.tree.height + 1)

    @_("NUMBER")
    def tree(self, p):
        return Tree(int(p.NUMBER), 0)

    @_("treelist tree")
    def treelist(self, p):
        return Treelist(
            p.treelist.sum + p.tree.val, max(p.treelist.height, p.tree.height)
        )

    @_("tree")
    def treelist(self, p):
        return Treelist(p.tree.val, p.tree.height)

    def error(self, p):
        print(rf"An error was found in line {p.lineno}".upper())
        if not p:
            print("End of File!")
            return

        while True:
            tok = next(self.tokens, None)
            if not tok:
                break
        self.restart()