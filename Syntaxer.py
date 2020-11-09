from Lexer import Lexer


class AST(object):
    pass


class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right


class Assign(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right


class UnarOp(AST):
    def __init__(self, op, expr):
        self.token = self.op = op
        self.expr = expr


class Read(AST):
    def __init__(self, expr):
        self.expr = expr


class Write(AST):
    def __init__(self, expr):
        self.expr = expr


class Case(AST):
    def __init__(self, case, select):
        self.expr = case
        self.select = select


class Selecter(AST):
    def __init__(self, id, expr):
        self.id = id
        self.expr = expr


class Var(AST):
    def __init__(self, token):
        self.token = token


class Num(AST):
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
        raise Exception('Syntax error: ' + msg)

    def eat(self, token_type):
        # compare the current token type with the passed token
        # type and if they match then "eat" the current token
        # and assign the next token to the self.current_token,
        # otherwise raise an exception.
        if self.current_token.type == token_type:
            self.current_token = self.tokens.pop(0)
        else:
            self.error(f"cannot resolve this token {str(self.current_token.val)} at line {str(self.current_token.line)}"
                       f" at column {str(self.current_token.column)}.  Expected {Lexer.NAMES[token_type]}")

    def program(self):
        """program : DECL DESC"""
        var_node = self.variable_declaration()
        desc_node = self.main_block()
        program_node = [var_node, desc_node]
        return program_node

    def variable_declaration(self):
        """var VLIST : integer;"""
        self.eat(Lexer.VAR)
        var_nodes = self.variable_list()
        self.eat(Lexer.COLON)
        self.eat(Lexer.INT)
        self.eat(Lexer.SEMICOLON)
        return var_nodes

    def variable_list(self):
        nodes = [Var(self.current_token)]  # first ID
        self.eat(Lexer.ID)
        while self.current_token.type == Lexer.COMMA:
            self.eat(Lexer.COMMA)
            nodes.append(Var(self.current_token))
            self.eat(Lexer.ID)
        return nodes

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
        while self.current_token.type in (Lexer.ID, Lexer.READ, Lexer.WRITE, Lexer.CASE):
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
        expr : term ((PLUS | MINUS) term)*
        """
        node = self.term()

        while self.current_token.type in (Lexer.PLUS, Lexer.MINUS):
            token = self.current_token
            if token.type == Lexer.PLUS:
                self.eat(Lexer.PLUS)
            elif token.type == Lexer.MINUS:
                self.eat(Lexer.MINUS)

            node = BinOp(left=node, op=token, right=self.term())

        return node

    def term(self):
        """term : factor ((DIV) factor)*"""
        node = self.factor()

        while self.current_token.type == Lexer.DIV:
            token = self.current_token
            self.eat(Lexer.DIV)

            node = BinOp(left=node, op=token, right=self.factor())

        return node

    def factor(self):
        """factor : MINUS factor
                  | CONST
                  | LPAREN expr RPAREN
                  | variable
        """
        token = self.current_token
        if token.type == Lexer.MINUS:
            self.eat(Lexer.MINUS)
            node = UnarOp(token, self.factor())
            return node
        elif token.type == Lexer.NUM:
            self.eat(Lexer.NUM)
            node = Num(token)
            return node
        elif token.type == Lexer.LPAR:
            self.eat(Lexer.LPAR)
            node = self.expr()
            self.eat(Lexer.RPAR)
            return node
        else:
            node = self.variable()
            return node

    def func(self):
        if self.current_token.type == Lexer.READ:
            self.eat(Lexer.READ)
            self.eat(Lexer.LPAR)
            id = self.variable_list()
            node = Read(id)
            self.eat(Lexer.RPAR)
        elif self.current_token.type == Lexer.WRITE:
            self.eat(Lexer.WRITE)
            self.eat(Lexer.LPAR)
            id = self.variable_list()
            node = Write(id)
            self.eat(Lexer.RPAR)
        elif self.current_token.type == Lexer.CASE:
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