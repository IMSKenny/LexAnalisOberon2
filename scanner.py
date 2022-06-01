# Лексический анализатор (сканер)

import string
from enum import Enum
import text
import error
import loc


class Lex(Enum):
    IDENT, NUMINT, NUMREAL, MODULE, IMPORT, BEGIN, END, CONST, TWODOT, \
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
comm = ""
locCount = 0
strChar = ""
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
intCount = 0  # счетчик целых
realCount = 0  # счетчик вещественных
charCount = 0  # счетчик символов
strCount = 0  # счетчик строк
keywordsCount = 0  # счетчик ключевых(зарезервированных) слов
identCount = 0  # счетчик идентификаторов
write_file = "-" * 54 + text.chEOL + "Лексический анализатор языка программирования Оберон-2 " + text.chEOL + "-" * 54

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
    global lex, ident, keywordsCount, identCount, strChar

    ident = text.ch  # Первая буква
    strChar += text.ch
    text.nextCh()
    while text.ch in string.ascii_letters + string.digits:
        ident += text.ch
        strChar += text.ch
        text.nextCh()
    lex = _kw.get(ident, Lex.IDENT)
    if lex == Lex.IDENT:
        identCount += 1
        dictionary(identLex, ident)
    else:
        keywordsCount += 1
        dictionary(keywordsLex, ident)


# распознавание чисел(целые и вещественные) и закодированных символов
def scanNumber():
    global num, lex, intCount, realCount, charCount, locCount, signCount, strChar
    num = 0
    numED = 0
    numReal = 0
    while text.ch in string.digits:
        if num <= (MAXINT - int(text.ch)) // 10:
            num = 10 * num + int(text.ch)
        else:
            num = str(num)
            strChar = str(num)
            loc.posEr = loc.pos
            while text.ch not in {text.chEOL, text.chEOT, text.chSPACE}:
                num += text.ch
                strChar += text.ch
                text.nextCh()
            print(num)
            # print(strChar)
            # print(loc.posEr)
            error.lexError3("Слишком большое число")
            loc.posWord = 0
            if strChar == text.chEOL:
                strChar = ""
        text.nextCh()
    if text.ch in {"A", "B", "C", "D", "E", "F"}:
        while text.ch in string.digits or text.ch in {"A", "B", "C", "D", "E", "F"}:
            num = str(num) + text.ch
            loc.posEr = loc.pos
            text.nextCh()
        strChar += str(num)
        if text.ch == 'H':
            num += text.ch
            strChar += text.ch
            # print(strChar)
            lex = Lex.NUMINT
            intCount += 1
            dictionary(intLex, num)
            text.nextCh()
        elif text.ch == 'X':
            num += text.ch
            strChar += text.ch
            lex = Lex.CHAR
            charCount += 1
            dictionary(charLex, num)
            text.nextCh()
        else:
            while text.ch not in {text.chEOL, text.chEOT, text.chSPACE}:
                num = str(num) + text.ch
                strChar += text.ch
                text.nextCh()
                locCount += 1
            # strChar += str(num)
            locCount += 1
            loc.posWord -= locCount - 2
            loc.posEr += 1
            # print(num)
            print(strChar)
            error.expect3("'H', либо 'X'")
            loc.posWord = 0
            locCount = 0
            if strChar == text.chEOL:
                strChar = ""
    elif text.ch == '.':
        text.nextCh()
        num = str(num) + '.'
        strChar += str(num)
        if text.ch in string.digits:
            while text.ch in string.digits:
                if numReal <= (MAXINT - int(text.ch)) // 10:
                    numReal = 10 * numReal + int(text.ch)
                else:
                    num = str(num) + str(numReal)
                    strChar += str(numReal)
                    loc.posEr = loc.pos
                    while text.ch not in {text.chEOL, text.chEOT, text.chSPACE}:
                        num += text.ch
                        strChar += text.ch
                        text.nextCh()
                    # print(num)
                    print(strChar)
                    error.lexError3("Слишком большое число после точки")
                    loc.posWord = 0
                    if strChar == text.chEOL:
                        strChar = ""
                text.nextCh()
            num = str(num) + str(numReal)
            # strChar += str(num)
            strChar += str(numReal)
        if text.ch in {'E', 'D'}:
            ed = text.ch
            num = str(num) + text.ch
            strChar += text.ch
            text.nextCh()
            if text.ch in {'+', '-'}:
                if text.ch == '-':
                    num += '-'
                    strChar += '-'
                else:
                    num += '+'
                    strChar += '+'
                text.nextCh()
            if text.ch in string.digits:
                while text.ch in string.digits:
                    if numED <= (MAXINT - int(text.ch)) // 10:
                        numED = 10 * numED+ int(text.ch)
                    else:
                        num = str(num) + str(numED)
                        strChar += str(numED)
                        loc.posEr = loc.pos
                        while text.ch not in {text.chEOL, text.chEOT, text.chSPACE}:
                            num += text.ch
                            strChar += text.ch
                            text.nextCh()
                        print(strChar)
                        error.lexError3("Слишком большое число после " + str(ed))
                        loc.posWord = 0
                    text.nextCh()
                num = str(num) + str(numED)
                strChar += str(numED)
            else:
                loc.posEr = loc.pos
                while text.ch not in {text.chEOL, text.chEOT, text.chSPACE}:
                    num += text.ch
                    text.nextCh()
                    locCount += 1
                loc.posWord -= locCount - 1
                print(strChar)
                error.expect3("цифра")
                loc.posWord = 0
                locCount = 0
        if text.ch == '.':
            signCount += 1
            dictionary(signsLex, '..')
            intCount += 1
            dictionary(intLex, num)
            strChar += '.'
            text.nextCh()
        else:
            num = str(num) + '.'
            # strChar += str(num)
            lex = Lex.NUMREAL
            realCount += 1
            dictionary(realLex, num)
    elif text.ch == 'X':
        num = str(num) + text.ch
        strChar += str(num)
        lex = Lex.CHAR
        charCount += 1
        dictionary(charLex, num)
        text.nextCh()
    elif text.ch == 'H':
        num = str(num) + text.ch
        strChar += str(num)
        lex = Lex.NUMINT
        intCount += 1
        dictionary(intLex, num)
        text.nextCh()
    else:
        strChar += str(num)
        lex = Lex.NUMINT
        intCount += 1
        dictionary(intLex, num)




# распознавание комментариев
def Comment():
    global comm, strChar

    comm += text.ch
    strChar += text.ch
    text.nextCh()  # *
    while True:
        while text.ch not in {'*', text.chEOT, '('}:
            comm += text.ch
            strChar += text.ch
            text.nextCh()
            loc.posEr = loc.pos
        if text.ch == text.chEOT:
            loc.posEr += 1
            print(strChar)
            error.lexError3("Не закончен комментарий")
        elif text.ch == '*':
            comm += text.ch
            strChar += text.ch
            text.nextCh()
            if text.ch == ')':
                comm += text.ch
                strChar += text.ch
                text.nextCh()
                break
        else:
            comm += text.ch
            strChar += text.ch
            text.nextCh()
            if text.ch == '*':
                Comment()


# распознавание строк
def stringLine():
    global strings, lex, strCount, strChar, strChar

    strings = ''
    if text.ch == '"':
        strings += text.ch
        strChar += text.ch
        text.nextCh()
        while text.ch not in {'"', text.chEOT}:
            # if text.ch == "\\":
            #     # print(strings)
            #     strings += text.ch
            #     text.nextCh()
            #     if text.ch == '"' or "'":
            #         strings += text.ch
            #         text.nextCh()
            strings += text.ch
            strChar += text.ch
            text.nextCh()
        if text.ch == text.chEOT:
            loc.posEr = loc.pos
            while text.ch not in {text.chEOL, text.chEOT, text.chSPACE}:
                text.nextCh()
                strings += text.ch
                strChar += text.ch
            loc.posEr += 1
            print(strChar)
            error.lexError3("Не закончена строка")
        if text.ch == '"':
            strings += text.ch
            strChar += text.ch
            text.nextCh()
            lex = Lex.STR
            strCount += 1
            dictionary(strLex, strings)
        else:
            loc.posEr = loc.pos
            while text.ch not in {text.chEOL, text.chEOT, text.chSPACE}:
                text.nextCh()
                strings += text.ch
                strChar += text.ch
            loc.posEr += 1
            print(strChar)
            error.lexError3("Нет разделителя после строки")

    elif text.ch == "'":
        strings += text.ch
        strChar += text.ch
        text.nextCh()
        while text.ch not in {"'", text.chEOT}:
            # if text.ch == '\\':
            #     strings += text.ch
            #     text.nextCh()
            #     if text.ch == "'" or '"':
            #         strings += text.ch
            #         text.nextCh()
            strings += text.ch
            strChar += text.ch
            text.nextCh()
        if text.ch == text.chEOT:
            loc.posEr = loc.pos
            while text.ch not in {text.chEOL, text.chEOT, text.chSPACE}:
                text.nextCh()
                strings += text.ch
                strChar += text.ch
            loc.posEr += 1
            print(strChar)
            error.lexError3("Не закончена строка")
        if text.ch == "'":
            strings += text.ch
            strChar += text.ch
            text.nextCh()
            lex = Lex.STR
            strCount += 1
            dictionary(strLex, strings)
        else:
            loc.posEr = loc.pos
            while text.ch not in {text.chEOL, text.chEOT, text.chSPACE}:
                text.nextCh()
                strings += text.ch
                strChar += text.ch
            loc.posEr += 1
            print(strChar)
            error.lexError3("Нет разделителя после строки")


# распознавание лексемы
def nextLex():
    global lex, signCount, comm, strChar

    loc.lexPos = loc.pos
    while text.ch in {text.chSPACE, text.chTAB, text.chEOL}:
        if text.ch == text.chSPACE:
            strChar += text.chSPACE
        if text.ch == text.chTAB:
            strChar += text.chTAB
        if text.ch == text.chEOL:
            strChar = ""
        text.nextCh()
        loc.posWord = 0
    if text.ch in string.ascii_letters:
        scanIdent()
    elif text.ch in string.digits:
        scanNumber()
    elif text.ch == ';':
        strChar += text.ch
        lex = Lex.SEMI
        signCount += 1
        dictionary(signsLex, ';')
        text.nextCh()
    elif text.ch in {"'", '"'}:
        stringLine()
    elif text.ch == '(':
        comm += text.ch
        strChar += text.ch
        text.nextCh()
        if text.ch == '*':
            Comment()
            nextLex()
        else:
            # strChar += '('
            lex = Lex.LPAR
            signCount += 1
            dictionary(signsLex, '(')
    elif text.ch == ')':
        strChar += text.ch
        lex = Lex.RPAR
        signCount += 1
        dictionary(signsLex, ')')
        text.nextCh()
    elif text.ch == ',':
        strChar += text.ch
        lex = Lex.COMMA
        signCount += 1
        dictionary(signsLex, ',')
        text.nextCh()
    elif text.ch == '.':
        text.nextCh()
        if text.ch == '.':
            strChar += text.ch + '.'
            lex = Lex.TWODOT
            signCount += 1
            dictionary(signsLex, '..')
            text.nextCh()
        else:
            strChar += '.'
            lex = Lex.DOT
            signCount += 1
            dictionary(signsLex, '.')
    elif text.ch == ':':
        text.nextCh()
        if text.ch == '=':
            strChar += ':='
            lex = Lex.ASS
            signCount += 1
            dictionary(signsLex, ':=')
            text.nextCh()
        else:
            strChar += ':'
            lex = Lex.COLON
            signCount += 1
            dictionary(signsLex, ':')
    elif text.ch == '>':
        text.nextCh()
        if text.ch == '=':
            strChar += '>='
            lex = Lex.GE
            signCount += 1
            dictionary(signsLex, '>=')
            text.nextCh()
        else:
            strChar += '>'
            lex = Lex.GT
            signCount += 1
            dictionary(signsLex, '>')
    elif text.ch == '<':
        text.nextCh()
        if text.ch == '=':
            strChar += '<='
            lex = Lex.LE
            signCount += 1
            dictionary(signsLex, '<=')
            text.nextCh()
        else:
            strChar += '<'
            lex = Lex.LT
            signCount += 1
            dictionary(signsLex, '<')
    elif text.ch == '=':
        strChar += text.ch
        lex = Lex.EQ
        signCount += 1
        dictionary(signsLex, '=')
        text.nextCh()
    elif text.ch == '#':
        strChar += text.ch
        lex = Lex.NE
        signCount += 1
        dictionary(signsLex, '#')
        text.nextCh()
    elif text.ch == '+':
        strChar += text.ch
        lex = Lex.PLUS
        signCount += 1
        dictionary(signsLex, '+')
        text.nextCh()
    elif text.ch == '-':
        strChar += text.ch
        lex = Lex.MINUS
        signCount += 1
        dictionary(signsLex, '-')
        text.nextCh()
    elif text.ch == '*':
        strChar += text.ch
        lex = Lex.MULT
        signCount += 1
        dictionary(signsLex, '*')
        text.nextCh()
    elif text.ch == '^':
        strChar += text.ch
        lex = Lex.CARET
        dictionary(signsLex, '^')
        text.nextCh()
    elif text.ch == '~':
        strChar += text.ch
        lex = Lex.TILDE
        dictionary(signsLex, '~')
        text.nextCh()
    elif text.ch == '&':
        strChar += text.ch
        lex = Lex.AMPERSAND
        signCount += 1
        dictionary(signsLex, '&')
        text.nextCh()
    elif text.ch == '|':
        strChar += text.ch
        lex = Lex.PIPELINE
        signCount += 1
        dictionary(signsLex, '|')
        text.nextCh()
    elif text.ch == '[':
        strChar += text.ch
        lex = Lex.LBRACKET
        signCount += 1
        dictionary(signsLex, '[')
        text.nextCh()
    elif text.ch == ']':
        strChar += text.ch
        lex = Lex.RBRACKET
        signCount += 1
        dictionary(signsLex, ']')
        text.nextCh()
    elif text.ch == '{':
        strChar += text.ch
        lex = Lex.LBRACES
        signCount += 1
        dictionary(signsLex, '{')
        text.nextCh()
    elif text.ch == '}':
        strChar += text.ch
        lex = Lex.RBRACES
        signCount += 1
        dictionary(signsLex, '}')
        text.nextCh()
    elif text.ch == '/':
        strChar += text.ch
        lex = Lex.SLASH
        signCount += 1
        dictionary(signsLex, '/')
        text.nextCh()
    elif text.ch == text.chEOT:
        lex = Lex.EOT
    else:
        strChar += text.ch
        print(strChar)
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

    for i in range(begin + 1, end + 1):
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
    write_file += "   Относительная частота лексем: " + str(round(count_lex / all_lex, 2)) + text.chEOL + text.chEOL
    write_file += '-' * 45 + text.chEOL
    write_file += ' ' * 2 + "Классы лексем    Частота    Относительная" + text.chEOL
    write_file += ' ' * 33 + "частота" + text.chEOL
    write_file += '-' * 45 + text.chEOL
    for k, v in dist_lex.items():
        write_file += ' ' * (15 - len(str(k))) + str(k) + ' ' * 7 + str(v) + ' ' * (13 - len(str(v))) + \
                      str(round(v / count_lex, 2)) + text.chEOL
    write_file += '-' * 45 + text.chEOL




def writeValueSort(class_lex, dist_lex, count_lex, all_lex):
    global write_file

    id = list(identLex)
    quick_sort(id)
    write_file += "Вариант Д:"
    write_file += text.chEOL + class_lex + text.chEOL
    # write_file += "   Абсолютная частота лексем:    " + str(count_lex) + text.chEOL
    # write_file += "   Относительная частота лексем: " + str(round(count_lex/all_lex, 2)) + text.chEOL + text.chEOL
    write_file += '-' * 53 + text.chEOL
    write_file += ' ' * 8 + "Лексемы     Частота    Относительная" + text.chEOL
    write_file += ' ' * 34 + "частота" + text.chEOL
    write_file += '-' * 53 + text.chEOL
    for k in id:
        write_file += ' ' * (15 - len(str(k))) + str(k) + ' ' * 8 + str(dist_lex.get(k)) + \
                      ' ' * (13 - len(str(dist_lex.get(k)))) + str(
            round((dist_lex.get(k) / count_lex) * 100, 2)) + '%' + text.chEOL
    write_file += '-' * 53 + text.chEOL


def relFrequency(count, allLex):
    if allLex == 0:
        return "0"
    else:
        return str(round((count / allLex) * 100, 2)) + "%"


def writeValueInTable(dist_lex, all_lex):
    global write_file

    for k, v in dist_lex.items():
        write_file += ' ' * (15 - len(str(k))) + str(k) + ' ' * 7 + str(v) + ' ' * (13 - len(str(v))) + \
                      relFrequency(v, all_lex) + text.chEOL


def calcScan():
    global write_file


    text.nextCh()
    nextLex()
    all_l = calcLex()
    write_file += text.chEOL
    write_file += "Обработаны файлы: " + text.chEOL + text.listfile + text.chEOL + text.chEOL
    write_file += "Вариант А:" + text.chEOL
    write_file += "Общее число лексем - " + str(all_l) + text.chEOL + text.chEOL
    write_file += "Вариант Б:" + text.chEOL
    write_file += "Подсчет частоты лексем каждого класса" + text.chEOL
    write_file += '-' * 45 + text.chEOL
    write_file += ' ' * 2 + "Классы лексем    Частота    Относительная" + text.chEOL
    write_file += ' ' * 33 + "частота" + text.chEOL
    write_file += '-' * 45 + text.chEOL
    write_file += ' ' * (15 - len('Целые')) + 'Целые' + ' ' * 7 + str(intCount) + \
                  ' ' * (13 - len(str(intCount))) + relFrequency(intCount, all_l) + text.chEOL
    write_file += ' ' * (15 - len('Вещественные')) + 'Вещественные' + ' ' * 7 + str(realCount) + \
                  ' ' * (13 - len(str(realCount))) + relFrequency(realCount, all_l) + text.chEOL
    write_file += ' ' * (15 - len('Символы')) + 'Символы' + ' ' * 7 + str(charCount) + \
                  ' ' * (13 - len(str(charCount))) + relFrequency(charCount, all_l) + text.chEOL
    write_file += ' ' * (15 - len('Строки')) + 'Строки' + ' ' * 7 + str(strCount) + ' ' * (13 - len(str(strCount))) + \
                  relFrequency(strCount, all_l) + text.chEOL
    write_file += ' ' * (15 - len('Идентификаторы')) + 'Идентификаторы' + ' ' * 7 + str(identCount) + \
                  ' ' * (13 - len(str(identCount))) + relFrequency(identCount, all_l) + text.chEOL
    writeValueInTable(keywordsLex, all_l)
    writeValueInTable(signsLex, all_l)
    write_file += '-' * 45 + text.chEOL + text.chEOL
    # writeValue('ЦЕЛЫЕ', intLex, intCount, all_l)
    # writeValue('ВЕЩЕСТВЕННЫЕ', realLex, realCount, all_l)
    # writeValue('СИМВОЛЫ', charLex, charCount, all_l)
    # writeValue('СТРОКИ', strLex, strCount, all_l)
    # writeValue('ЗНАКИ', signsLex, signCount, all_l)
    # writeValue('ЗАРЕЗЕРВИРОВАННЫЕ СЛОВА', keywordsLex, keywordsCount, all_l)
    writeValueSort('Перечень идентификаторов в лексикографическом порядке', identLex, identCount, all_l)