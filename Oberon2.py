# Компилятор языка "О"
import scanner
import text


print(text.chEOL + 'Лексический анализатор языка программирования Оберон-2' + text.chEOL + "-"*53)
text.Reset()
scanner.calcScan()
text.safeFile(scanner.write_file)
print("Программа завершена успешно.")
print("Результат записан в файл: ", text.sys.argv[2])

