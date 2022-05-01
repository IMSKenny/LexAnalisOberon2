# Лексический анализатор (сканер)

import string
from enum import Enum
import text
import error
import loc



class Lex(Enum):
    IDENT, NUMINT, NUMREAL, MODULE, IMPORT, BEGIN, END, CONST, TWODOT,\
    BY, STR, CHAR, VAR, WHILE, DO, IF, THEN, ELSIF, ELSE, MULT, DIV, MOD, \
    CASE, EXIT, FOR, ARRAY, IN, IS, LOOP, NIL, OF, OR, POINTER, PROCEDURE, \
    RECORD, REPEAT, RETURN, PLUS, MINUS, EQ, NE, LT, LE, GT, GE, DOT, COMMA, \
    LBRACKET, RBRACKET, LBRACES, RBRACES, PIPELINE, AMPERSAND, TILDE, CARET, \
    SLASH, TO, TYPE, UNTIL, WITH, COLON, SEMI, ASS, LPAR, RPAR, SET, EOT = range(67)


MAXINT = 0x7FFFFFFF
lex = Lex.MODULE
num = 0
ident = ""
strings = ""
identLex = dict()
keywordsLex = dict()
signsLex = dict()
realLex = dict()
intLex = dict()
charLex = dict()
strLex = dict()
# whitespace_count = 0  # счетчик пустых разделителей
# signCount = 0  # счетчик разделителей
signCount = 0  # счетчик знаков
constant_count = 0  # счетчик констант
keyword_count = 0  # счетчик ключевых(зарезервированных) слов
ident_count = 0  # счетчик идентификаторов
write_file = "-"*54 + text.chEOL + "Лексический анализатор языка программирования Оберон-2 " + text.chEOL + "-"*54


# словарь ключевых слов
_kw = {
    'MODULE': Lex.MODULE,
    'IMPORT': Lex.IMPORT,
    "CONST": Lex.CONST,
    "VAR": Lex.VAR,
    "BEGIN": Lex.BEGIN,
    "END": Lex.END,
    "IF": Lex.IF,
    "THEN": Lex.THEN,
    "ELSIF": Lex.ELSIF,
    "ELSE": Lex.ELSE,
    "WHILE": Lex.WHILE,
    "DO": Lex.DO,
    "DIV": Lex.DIV,
    "MOD": Lex.MOD,
    "ARRAY": Lex.ARRAY,
    "RECORD": Lex.RECORD,
    "POINTER": Lex.POINTER,
    "SET": Lex.SET,
    "WITH": Lex.WITH,
    "CASE": Lex.CASE,
    "OF": Lex.OF,
    "LOOP": Lex.LOOP,
    "EXIT": Lex.EXIT,
    "PROCEDURE": Lex.PROCEDURE,
    "FOR": Lex.FOR,
    "TO": Lex.TO,
    "BY": Lex.BY,
    "IN": Lex.IN,
    "IS": Lex.IS,
    "NIL": Lex.NIL,
    "OR": Lex.OR,
    "TYPE": Lex.TYPE,
    "REPEAT": Lex.REPEAT,
    "UNTIL": Lex.UNTIL,
    "RETURN": Lex.RETURN
}


# словарь для вывода имен лексем
_names = {
    Lex.IDENT: 'идентификатор',
    Lex.NUMINT: 'целое число',
    Lex.NUMREAL: 'вещественное число',
    Lex.STR: 'строка',
    Lex.CHAR: 'символ',
    Lex.MULT: '"*"',
    Lex.PLUS: '"+"',
    Lex.MINUS: '"-"',
    Lex.EQ: '"="',
    Lex.NE: '"#"',
    Lex.LT: '"<"',
    Lex.LE: '"<="',
    Lex.GT: '">"',
    Lex.GE: '">="',
    Lex.DOT: '"."',
    Lex.COMMA: '","',
    Lex.COLON: '":"',
    Lex.SEMI: '";"',
    Lex.ASS: '":="',
    Lex.LPAR: '"("',
    Lex.RPAR: '")"',
    Lex.EOT: 'конец текста',
    Lex.CARET: '"^"',
    Lex.TILDE: '"~"',
    Lex.AMPERSAND: '"&"',
    Lex.PIPELINE: '"|"',
    Lex.LBRACKET: '"["',
    Lex.RBRACKET: '"]"',
    Lex.LBRACES: '"{"',
    Lex.RBRACES: '"}"',
    Lex.SLASH: '"/"',
    Lex.TWODOT: '".."'
    
}


# заполнение словаря лексемами определенного класса и подсчет их количества
def dictionary(name_dist, value):
    if value in name_dist:
        name_dist[value] += 1
    else:
        name_dist[value] = 1


# вывод названия лексемы
def lexName(L):
    return _names.get(L, L.name)


# распознавание идентификаторов и зарезервированных слов
def scanIdent():
    global lex, ident, keyword_count, ident_count

    ident = text.ch  # Первая буква
    text.nextCh()
    while text.ch in string.ascii_letters + string.digits:
        ident += text.ch
        text.nextCh()
    lex = _kw.get(ident, Lex.IDENT)
    if lex == Lex.IDENT:
        ident_count += 1
        dictionary(identLex, ident)
    else:
        keyword_count += 1
        dictionary(keywordsLex, ident)


# распознавание чисел(целые, вещественные, шестнадцатеричных) и закодированных символов
def scanNumber():
    global num, lex, constant_count

    num = 0
    num_real = 0
    ed = 0
    sign = 1
    while text.ch in string.digits:
        if num <= (MAXINT - int(text.ch)) // 10:
            num = 10 * num + int(text.ch)
        else:
            num = str(num)
            while text.ch not in {text.chEOL, text.chEOT, text.chSPACE}:
                text.nextCh()
                num += text.ch
            print(num)
            error.lexError("Слишком большое число")
        text.nextCh()
    if text.ch in {"A", "B", "C", "D", "E", "F"}:
        while text.ch in {"A", "B", "C", "D", "E", "F"} or (text.ch in string.digits):
            num = str(num) + text.ch
            text.nextCh()
        if text.ch == 'H':
            num = str(num) + text.ch
            text.nextCh()
            if text.ch not in string.ascii_letters:
                lex = Lex.NUMINT
                constant_count += 1
            else:
                num = str(num)
                while text.ch not in {text.chEOL, text.chEOT, text.chSPACE}:
                    text.nextCh()
                    num += text.ch
                print(num)
                error.lexError("Неверно задано шестнадцатеричное число, либо символ")
        elif text.ch == 'X':
            num = str(num) + text.ch
            text.nextCh()
            if text.ch not in string.ascii_letters:
                lex = Lex.CHAR
                constant_count += 1
            else:
                num = str(num)
                while text.ch not in {text.chEOL, text.chEOT, text.chSPACE}:
                    text.nextCh()
                    num += text.ch
                print(num)
                error.lexError("Неверно задано шестнадцатеричное число, либо символ")
        else:
            num = str(num)
            while text.ch not in {text.chEOL, text.chEOT, text.chSPACE}:
                text.nextCh()
                num += text.ch
            print(num)
            error.lexError("Неверно задано шестнадцатеричное число, либо символ")
    elif text.ch == '.':
        num = str(num) + text.ch
        text.nextCh()
        if text.ch in string.digits:
            while text.ch in string.digits:
                num += text.ch
                text.nextCh() 
        else:
            num = str(num)
            while text.ch not in {text.chEOL, text.chEOT, text.chSPACE}:
                text.nextCh()
                num += text.ch
            print(num)
            error.lexError("Неверно задано вещественное число")
        if text.ch in {'E', 'D'}:
            num_real = float(num)
            num = str(num) + text.ch
            text.nextCh() 
            if text.ch in {'+', '-'}:
                num += text.ch
                text.nextCh() 
                if text.ch == '-':
                    sign = -1
            if text.ch in string.digits:
                while text.ch in string.digits:
                    if ed <= (MAXINT - int(text.ch)) // 10:
                        ed = 10 * ed + int(text.ch)
                    else:
                        num = str(num + sign + ed)
                        while text.ch not in {text.chEOL, text.chEOT, text.chSPACE}:
                            text.nextCh()
                            num += text.ch
                        print(num)
                        error.lexError("Слишком большое число степени")
                    num += text.ch
                    text.nextCh()   
            else:
                num = str(num)
                while text.ch not in {text.chEOL, text.chEOT, text.chSPACE}:
                    text.nextCh()
                    num += text.ch
                print(num)
                error.lexError("Неверно задано вещественное число")
        lex = Lex.NUMREAL
        constant_count += 1
        num_real = num_real*sign*(10**ed)
    elif text.ch not in string.ascii_letters:                
        lex = Lex.NUMINT
        constant_count += 1
    else:
        num = str(num)
        while text.ch not in {text.chEOL, text.chEOT, text.chSPACE}:
            text.nextCh()
            num += text.ch
        print(num)
        error.lexError("Неверно задано число")
    dictionary(intLex, num)


# распознавание комментариев
def Comment():
    text.nextCh()  # *
    while True:
        while text.ch not in {'*', text.chEOT, '('}:
            text.nextCh()
        if text.ch == text.chEOT:
            error.lexError("Не закончен комментарий")
        elif text.ch == '*':
            text.nextCh()
            if text.ch == ')':
                text.nextCh()
                break
        else:
            text.nextCh()
            if text.ch == '*':
                Comment()


# распознавание строк
def stringLine():
    global strings, lex

    strings = ''
    if text.ch == '"':
        strings += text.ch
        text.nextCh()
        while text.ch not in {'"', text.chEOT}:
            if text.ch == "\\":
                strings += text.ch
                text.nextCh()
                if text.ch == '"' or "'":
                    strings += text.ch
                    text.nextCh()                
            strings += text.ch
            text.nextCh()
        if text.ch == text.chEOT:
            while text.ch not in {text.chEOL, text.chEOT, text.chSPACE}:
                text.nextCh()
                strings += text.ch
            print(strings)
            error.lexError("Не закончена строка")
        if text.ch == '"':
            strings += text.ch
            text.nextCh()
            lex = Lex.STR
        else:
            while text.ch not in {text.chEOL, text.chEOT, text.chSPACE}:
                text.nextCh()
                strings += text.ch
            print(strings)
            error.lexError("Нет разделителя после строки")
            
    elif text.ch == "'":
        strings += text.ch
        text.nextCh()
        while text.ch not in {"'", text.chEOT}:
            if text.ch == '\\':
                strings += text.ch
                text.nextCh()
                if text.ch == "'" or '"':
                    strings += text.ch
                    text.nextCh()                
            strings += text.ch
            text.nextCh()
        if text.ch == text.chEOT:
            while text.ch not in {text.chEOL, text.chEOT, text.chSPACE}:
                text.nextCh()
                strings += text.ch
            print(strings)
            error.lexError("Не закончена строка")
        if text.ch == "'":
            strings += text.ch
            text.nextCh()
            lex = Lex.STR
        else:
            while text.ch not in {text.chEOL, text.chEOT, text.chSPACE}:
                text.nextCh()
                strings += text.ch
            print(strings)
            error.lexError("Нет разделителя после строки")
    dictionary(strLex, strings)
            

# распознавание лексемы
def nextLex():
    global lex, signCount

    loc.lexPos = loc.pos
    while text.ch in {text.chSPACE, text.chTAB, text.chEOL}:
        text.nextCh()
    if text.ch in string.ascii_letters:
        scanIdent()
    elif text.ch in string.digits:
        scanNumber()
    elif text.ch == ';':
        lex = Lex.SEMI
        signCount += 1
        dictionary(signsLex, ';')
        text.nextCh()
    elif text.ch in {"'", '"'}:
        stringLine()
    elif text.ch == '(':
        text.nextCh()
        if text.ch == '*':
            Comment()
            nextLex()
        else:
            lex = Lex.LPAR
            signCount += 1
            dictionary(signsLex, '(')
    elif text.ch == ')':
        lex = Lex.RPAR
        signCount += 1
        dictionary(signsLex, ')')
        text.nextCh()
    elif text.ch == ',':
        lex = Lex.COMMA
        signCount += 1
        dictionary(signsLex, ',')
        text.nextCh()
    elif text.ch == '.':
        text.nextCh()
        if text.ch == '.':
            lex = Lex.TWODOT
            signCount += 1
            signCount += 1
            dictionary(signsLex, '..')
            text.nextCh()
        else:
            lex = Lex.DOT
            signCount += 1
            dictionary(signsLex, '.')
    elif text.ch == ':':
        text.nextCh()
        if text.ch == '=':
            lex = Lex.ASS
            signCount += 1
            dictionary(signsLex, ':=')
            text.nextCh()
        else:
            lex = Lex.COLON
            signCount += 1
            dictionary(signsLex, ':')
    elif text.ch == '>':
        text.nextCh()
        if text.ch == '=':
            lex = Lex.GE
            signCount += 1
            dictionary(signsLex, '>=')
            text.nextCh()
        else:
            lex = Lex.GT
            signCount += 1
            dictionary(signsLex, '>')
    elif text.ch == '<':
        text.nextCh()
        if text.ch == '=':
            lex = Lex.LE
            signCount += 1
            dictionary(signsLex, '<=')
            text.nextCh()
        else:
            lex = Lex.LT
            signCount += 1
            dictionary(signsLex, '<')
    elif text.ch == '=':
        lex = Lex.EQ
        signCount += 1
        dictionary(signsLex, '=')
        text.nextCh()
    elif text.ch == '#':
        lex = Lex.NE
        signCount += 1
        dictionary(signsLex, '#')
        text.nextCh()
    elif text.ch == '+':
        lex = Lex.PLUS
        signCount += 1
        dictionary(signsLex, '+')
        text.nextCh()
    elif text.ch == '-':
        lex = Lex.MINUS
        signCount += 1
        dictionary(signsLex, '-')
        text.nextCh()
    elif text.ch == '*':
        lex = Lex.MULT
        signCount += 1
        dictionary(signsLex, '*')
        text.nextCh()
    elif text.ch == '^':
        lex = Lex.CARET
        text.nextCh()
    elif text.ch == '~':
        lex = Lex.TILDE
        text.nextCh()
    elif text.ch == '&':
        lex = Lex.AMPERSAND
        signCount += 1
        dictionary(signsLex, '&')
        text.nextCh()
    elif text.ch == '|':
        lex = Lex.PIPELINE
        signCount += 1
        dictionary(signsLex, '|')
        text.nextCh()
    elif text.ch == '[':
        lex = Lex.LBRACKET
        signCount += 1
        dictionary(signsLex, '[')
        text.nextCh()
    elif text.ch == ']':
        lex = Lex.RBRACKET
        signCount += 1
        dictionary(signsLex, ']')
        text.nextCh()
    elif text.ch == '{':
        lex = Lex.LBRACES
        signCount += 1
        dictionary(signsLex, '{')
        text.nextCh()
    elif text.ch == '}':
        lex = Lex.RBRACES
        signCount += 1
        dictionary(signsLex, '}')
        text.nextCh()
    elif text.ch == '/':
        lex = Lex.SLASH
        signCount += 1
        dictionary(signsLex, '/')
        text.nextCh()
    elif text.ch == text.chEOT:
        lex = Lex.EOT
    else:
        print(text.ch)
        error.lexError("Недопустимый символ")


# подсчет общего количества лексем
def calcLex():
    n = 0

    while lex != Lex.EOT:
        n += 1
        nextLex()
    return n


def list(l):
    array = []

    for i in l.keys():
        array.append(i)
    return array


def partition(array, begin, end):
    pivot = begin

    for i in range(begin+1, end+1):
        if array[i] <= array[begin]:
            pivot += 1
            array[i], array[pivot] = array[pivot], array[i]
    array[pivot], array[begin] = array[begin], array[pivot]
    return pivot


def quick_sort(array, begin=0, end=None):
    if end is None:
        end = len(array) - 1
    def _quicksort(array, begin, end):
        if begin >= end:
            return
        pivot = partition(array, begin, end)
        _quicksort(array, begin, pivot - 1)
        _quicksort(array, pivot + 1, end)
    return _quicksort(array, begin, end)


def writeValue(class_lex, dist_lex, count_lex, all_lex):
    global write_file

    write_file += text.chEOL + text.chEOL + "Класс " + class_lex + text.chEOL
    write_file += "   Абсолютная частота лексем:    " + str(count_lex) + text.chEOL
    write_file += "   Относительная частота лексем: " + str(round(count_lex/all_lex, 2)) + text.chEOL + text.chEOL
    write_file += ' '*8 + "Лексемы   Частота  Относительная" + text.chEOL
    write_file += ' '*30 + "частота" + text.chEOL
    write_file += '-'*48 + text.chEOL
    for k, v in dist_lex.items():
        write_file += ' '*(15 - len(str(k))) + str(k) + ' '*6 + str(v) + ' '*(11 - len(str(v))) + \
                     str(round(v/count_lex, 2)) + text.chEOL


def writeValueSort(class_lex, dist_lex, count_lex, all_lex):
    global write_file

    id = list(identLex)
    quick_sort(id)
    write_file += "Вариант Д:"
    write_file += text.chEOL + class_lex + text.chEOL
    # write_file += "   Абсолютная частота лексем:    " + str(count_lex) + text.chEOL
    # write_file += "   Относительная частота лексем: " + str(round(count_lex/all_lex, 2)) + text.chEOL + text.chEOL
    write_file += '-' * 53 + text.chEOL
    write_file += ' '*8 + "Лексемы     Частота    Относительная" + text.chEOL
    write_file += ' '*34 + "частота" + text.chEOL
    write_file += '-'*53 + text.chEOL
    for k in id:
        write_file += ' '*(15 - len(str(k))) + str(k) + ' '*8 + str(dist_lex.get(k)) + \
                      ' '*(13 - len(str(dist_lex.get(k)))) + str(round(dist_lex.get(k)/count_lex, 2)) + text.chEOL
    write_file += '-' * 53 + text.chEOL


def calcScan():
    global write_file

    text.nextCh()
    nextLex()
    all_l = calcLex()
    write_file += text.chEOL
    write_file += "Обработаны файлы: " + text.chEOL + text.listfile + text.chEOL + text.chEOL
    write_file += "Вариант А:" + text.chEOL
    write_file += "Общее число лексем - " + str(all_l) + text.chEOL + text.chEOL
    writeValue('ЗНАКИ', signsLex, signCount, all_l)
    writeValue('ЦЕЛЫЕ', intLex, constant_count, all_l)
    writeValue('ВЕЩЕСТВЕННЫЕ', realLex, constant_count, all_l)
    writeValue('СИМВОЛЫ', charLex, constant_count, all_l)
    writeValue('СТРОКИ', strLex, constant_count, all_l)
    writeValue('ЗАРЕЗЕРВИРОВАННЫЕ СЛОВА', keywordsLex, keyword_count, all_l)
    writeValueSort('Перечень идентификаторов в лексикографическом порядке', identLex, ident_count, all_l)







