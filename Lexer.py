from Token import Token
import sys


class Lexer:

    # терминальный словарь
    NUM, ID, VAR, BEGIN, END, INT, CASE, OF, END_CASE, DIV, READ, WRITE, LPAR, RPAR, PLUS, MINUS, \
    EQUAL, SEMICOLON, DOT, COLON, COMMA, EOF = range(22)

    # специальные символы языка
    SYMBOLS = {'=': EQUAL, ';': SEMICOLON, '(': LPAR, ')': RPAR, '+': PLUS,
               '-': MINUS, '/': DIV, ',': COMMA, ':': COLON, '.': DOT}

    # ключевые слова
    WORDS = {'var': VAR, 'begin': BEGIN, 'end': END, 'integer': INT, 'read': READ, 'write': WRITE,
             'case': CASE, 'of': OF, 'end_case': END_CASE}

    # текущий символ, считанный из исходника
    ch = ' '  # допустим, первый символ - это пробел

    # конструктор
    def __init__(self, fname):
        self.f = open(fname, 'r')
        self.line = 1
        self.col = -1
        self.tok = Token(None, None, 0, 0)

        self.tokens = []


    def get_all_tokens(self):
        while self.tok.type != Lexer.EOF:
            self.next_tok()
            self.tokens.append(self.tok)
        self.f.close()

    # вывод сообщения об ошибке
    def error(self, msg):
        self.f.close()
        raise Exception('Lexer error: ', msg)

    # получить следующий символ
    def get_char(self):
        self.ch = self.f.read(1)
        self.col += 1

    # проверить что лежит в символе пробела
    def check_space(self):
        if self.ch == '\n':
            self.line += 1
            self.col = -1
        elif self.ch == '\t':
            self.col += 3

    # проверить следующий токе
    def next_tok(self):
        self.tok = None
        while self.tok is None:
            # конец файла
            if len(self.ch) == 0:
                self.tok = Token(None, Lexer.EOF, self.line, self.col)
            # пробельный символ
            elif self.ch.isspace():
                self.check_space()
                self.get_char()
            # спец символ
            elif self.ch in Lexer.SYMBOLS:
                self.tok = Token(self.ch, Lexer.SYMBOLS[self.ch], self.line, self.col)
                self.get_char()
            # число
            elif self.ch.isdigit():
                int_val = 0
                while self.ch.isdigit():
                    int_val = int_val * 10 + int(self.ch)
                    self.get_char()
                self.tok = Token(int_val, Lexer.NUM, self.line, self.col)
            # идентификатор переменной
            elif self.ch.isalpha() or self.ch == "_":
                ident = ''
                while self.ch.isalpha() or self.ch == "_":
                    ident = ident + self.ch.lower()
                    self.get_char()
                if ident in Lexer.WORDS:
                    self.tok = Token(ident, Lexer.WORDS[ident], self.line, self.col)
                elif len(ident) <= 9:
                    self.tok = Token(ident, Lexer.ID, self.line, self.col)
                else:
                    self.error('Unknown identifier: ' + ident + ' on line ' + str(self.line))
            else:
                self.error('Unexpected symbol: ' + self.ch + ' on line ' + str(self.line))