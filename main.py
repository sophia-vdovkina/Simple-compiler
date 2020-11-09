from Lexer import Lexer
from  Syntaxer import Syntaxer

def main():
    lex = Lexer('pr.txt')
    lex.get_all_tokens()
    print(lex.tokens)
    syn = Syntaxer(lex.tokens)
    tree = syn.parse()

if __name__ == '__main__':
    main()

