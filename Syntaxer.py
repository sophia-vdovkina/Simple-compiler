from Lexer import Lexer

class BinOp():
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right

class Assign():
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right

class UnarOp():
    def __init__(self, op, expr):
        self.token = self.op = op
        self.expr = expr

class Read():
    def __init__(self, expr):
        self.expr = expr

class Write():
    def __init__(self, expr):
        self.expr = expr

class Case():
    def __init__(self, case, select):
        self.expr = case
        self.select = select

class Selecter():
    def __init__(self, id, expr):
        self.id = id
        self.expr = expr

class Var():
    def __init__(self, token):
        self.token = token
        self.val = token.val

class Syntaxer:
    PROG, DECL, DESL, ALIST, VLIST, AS, UN, BIN, OP, CLIST, SELECT, FUNC, EXP, SUBEXP = range(14)

    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = tokens.pop(0)

    def parse(self):
        node = self.program()
        if self.current_token.type != Lexer.EOF:
            self.error('unresolved error')

        return node

    def error(self, msg):
        raise Exception('Syntax exception ' + msg)

    def eat(self, token_type):
        # compare the current token type with the passed token
        # type and if they match then "eat" the current token
        # and assign the next token to the self.current_token,
        # otherwise raise an exception.
        if self.current_token.type == token_type:
            self.current_token = self.tokens.pop(0)
        else:
            self.error("cannot resolve this token " + str(self.current_token.val) + " at line " + str(self.current_token.line))

    def program(self):
        """program : DECL DESC"""
        var_node = self.variable_declaration()
        desc_node = self.main_block()
        program_node = [var_node, desc_node]
        return program_node


    def variable_declaration(self):
        """var VLIST : integer;"""
        self.eat(Lexer.VAR)
        var_nodes = [Var(self.current_token)]  # first ID
        self.eat(Lexer.ID)
        var_nodes = [self.current_token]  # first ID
        self.eat(Lexer.ID)
        while self.current_token.type == Lexer.COMMA:
            self.eat(Lexer.COMMA)
            var_nodes.append(Var(self.current_token))
            self.eat(Lexer.ID)
        self.eat(Lexer.COLON)
        self.eat(Lexer.INT)
        self.eat(Lexer.SEMICOLON)
        return var_nodes

    def variable(self):
        """
        variable : ID
        """
        node = Var(self.current_token)
        self.eat(Lexer.ID)
        return node


    def main_block(self):
        """begin ALIST END"""
        self.eat(Lexer.BEGIN)
        nodes = self.statement_list()
        self.eat(Lexer.END)
        return nodes

    def statement_list(self):
        """
        ALIST : statement ALIST
                       | func ALIST | e
        """
        statements = []
        while self.current_token.type in (Lexer.ID, Lexer.READ, Lexer.READ, Lexer.CASE):
            if self.current_token.type == Lexer.ID:
                statements.append(self.assignment_statement())
            elif self.current_token.type in (Lexer.READ, Lexer.WRITE, Lexer.CASE):
                statements.append(self.func())
        return statements

    def assignment_statement(self):
        """
        assignment_statement : ID = EXP;
        """
        left = self.variable()
        token = self.current_token
        self.eat(Lexer.EQUAL)
        right = self.expr()
        node = Assign(left, token, right)
        self.eat(Lexer.SEMICOLON)
        return node

    def expr(self):
        """
        expr : subexp F' | - subexp
        """

        if self.current_token.type in (Lexer.LPAR, Lexer.ID, Lexer.NUM, Lexer.MINUS):
            if self.current_token.type == Lexer.MINUS:
                token = self.current_token
                self.eat(Lexer.MINUS)
                node = UnarOp(token, self.subexp())
                return node
            else:
                node = self.subexp()
                if self.current_token.type in (Lexer.MINUS, Lexer.PLUS, Lexer.DIV):
                    token = self.current_token
                    self.eat(self.current_token.type)
                    node = BinOp(left=node, op=token, right=self.subexp())
                return node

    def subexp(self):
        if self.current_token.type == Lexer.LPAR:
            self.eat(Lexer.LPAR)
            self.expr()
            self.eat(Lexer.RPAR)
        else:
            node = self.current_token
            if self.current_token.type == Lexer.ID:
                node = self.variable()
            else:
                self.eat(Lexer.NUM)
        return node

    def func(self):
        if self.current_token.type == Lexer.READ:
            self.eat(Lexer.READ)
            id = self.variable()
            node = Read(id)
        if self.current_token.type == Lexer.WRITE:
            self.eat(Lexer.WRITE)
            id = self.variable()
            node = Write(id)
        if self.current_token.type == Lexer.CASE:
            self.eat(Lexer.CASE)
            expr = self.expr()
            self.eat(Lexer.OF)
            sel = self.select()
            self.eat(Lexer.END_CASE)
            node = Case(expr, sel)
        self.eat(Lexer.SEMICOLON)
        return node

    def select(self):
        id = self.current_token
        self.eat(Lexer.NUM)
        self.eat(Lexer.COLON)
        node = [Selecter(id, self.assignment_statement())]

        while self.current_token.type == Lexer.NUM:
            id = self.current_token
            self.eat(Lexer.NUM)
            self.eat(Lexer.COLON)
            node.append(Selecter(id, self.assignment_statement()))
        return node