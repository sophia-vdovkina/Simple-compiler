from Lexer import Lexer

###############################################################################
#                                                                             #
#  AST visitors (walkers)                                                     #
#                                                                             #
###############################################################################

class NodeVisitor(object):
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))

###############################################################################
#                                                                             #
#  INTERPRETER                                                                #
#                                                                             #
###############################################################################

class Interpreter(NodeVisitor):
    def __init__(self, tree):
        self.tree = tree
        self.GLOBAL_MEMORY = {}

    def error(self, msg):
        raise Exception(f'Interpretation error: {msg}')

    def compile(self):
        if self.tree is None:
            return ''
        self.visit_VarDecl(self.tree[0])
        return self.visit_Statements(self.tree[1])

    def visit_VarDecl(self, node):
        for var in node:
            self.GLOBAL_MEMORY[var.token.val] = 0

    def visit_Statements(self, node):
        for st in node:
            self.visit(st)

    def visit_BinOp(self, node):
        if node.op.type == Lexer.PLUS:
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == Lexer.MINUS:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == Lexer.DIV:
            return self.visit(node.left) // self.visit(node.right)

    def visit_Num(self, node):
        return node.val

    def visit_UnarOp(self, node):
        op = node.op.type
        if op == Lexer.MINUS:
            return -self.visit(node.expr)

    def visit_Assign(self, node):
        var_name = node.left.token.val
        var_value = self.visit(node.right)
        self.GLOBAL_MEMORY[var_name] = var_value

    def visit_Var(self, node):
        var_name = node.token.val
        var_value = self.GLOBAL_MEMORY.get(var_name)
        return var_value

    def visit_Read(self, node):
        for var in node.expr:
            if var.token.val in self.GLOBAL_MEMORY:
                try:
                    self.GLOBAL_MEMORY[var.token.val] = int(input())
                except:
                    self.error('invalid type input for integer')
            else:
                self.error('cannot resolve reference: ' + str(var.token.val) + ' on line ' + str(var.token.line))

    def visit_Write(self, node):
        for var in node.expr:
            if (var.token.type == Lexer.ID) and (var.token.val in self.GLOBAL_MEMORY):
                print(str(self.GLOBAL_MEMORY[var.token.val]))
            else:
                self.error(f'unresolved variable {var.token.val}')

    def visit_Case(self, node):
        case = self.visit(node.expr)
        for select in node.select:
            if select.id.val == case:
                self.visit(select.expr)

