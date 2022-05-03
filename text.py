# Драйвер исходного текста

import glob
import sys
import loc
import error


chEOT = "\0"
chEOL = "\n"
chSPACE = ' '
chTAB = '\t'

_src = ""
_i = 0
ch = ""
listfile = ""


def Reset():
    global _src, listfile

    if len(sys.argv) != 3:
        error.Error("Запуск: python Oberon2.py <файл программы.ob2(.obn)> <файл результатов.txt>")
    else:
        try:
            if sys.argv[1] == '*.ob2':
                for file in glob.glob("*.ob2"):
                    _f = open(file)
                    _src = _src + _f.read()
                    _f.close()
                    listfile += file + chEOL
            elif sys.argv[1] == '*.o':
                for file in glob.glob("*.o"):
                    _f = open(file)
                    _src = _src + _f.read()
                    _f.close()
                    listfile += file + chEOL
            else:
                _f = open(sys.argv[1])
                _src = _f.read()
                _f.close()
                listfile = sys.argv[1]
        except:
            error.Error("Ошибка открытия файла")


def safeFile(sf):
    _wf = open(sys.argv[2], "w")
    _wf.write(sf)

def nextCh():
    global _src, _i, ch

    if _i < len(_src):
        ch = _src[_i]
        # print(ch, end="")
        loc.pos += 1
        loc.posWord += 1
        _i += 1
        # if ch == chSPACE:
        #     loc.posWord = 0
        if ch in {'\n', '\r'}:
            ch = chEOL
            loc.pos = 0
    else:
        ch = chEOT


