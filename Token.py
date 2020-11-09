class Token:
    def __init__(self, val, type, line, column):
        self.line = line
        self.column = column
        self.val = val
        self.type = type

    def __repr__(self):
        return f'строка {self.line} столбец {self.column} значение {self.val} тип {self.type} \n'
