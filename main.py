import sys

from Lexer import Lexer
from Syntaxer import Syntaxer
from Interpreter import Interpreter

def main():
    lex = Lexer('pr.txt')

    try:
        lex.get_all_tokens()
        syn = Syntaxer(lex.tokens)
        tree = syn.parse()
        interpreter = Interpreter(tree)
        interpreter.compile()
    except Exception as err:
        print(str(err), file=sys.stderr)



if __name__ == '__main__':
    main()

