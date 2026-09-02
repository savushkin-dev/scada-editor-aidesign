# errors.py
# Понятные сообщения об ошибках.
#
# Пользователю показывали то, что сказала библиотека:
#
#   Cannot open empty file: filename='C:/Users/.../пустой.pdf'
#   Failed to open file 'C:/Users/.../не_pdf.pdf'
#   error loading code: [string "<python>"]:88: unfinished string near <eof>
#
# По таким строкам нельзя понять ни что случилось, ни что теперь делать.
# Здесь они превращаются в объяснение на русском с подсказкой, куда смотреть.
#
# Собственные сообщения проекта («В Lua-файле не найден блок nodes»,
# «В PDF нет страницы 99 (всего 1)») уже написаны по делу — они проходят
# как есть, переписывать их незачем.
import re
from typing import Optional

# Ошибки библиотек узнаём по имени класса. Импортировать ради этого fitz
# и lupa нельзя: модуль должен оставаться лёгким и годиться для тех мест,
# где ни PyMuPDF, ни Lua не загружены.
LIBRARY_MESSAGES = {
    # PyMuPDF
    "EmptyFileError": "Файл пуст. Возможно, выгрузка чертежа не завершилась.",
    "FileDataError": "Это не PDF или файл повреждён. "
                     "Проверьте, что выбран нужный файл.",
    "FileNotFoundError": "Файл не найден. Возможно, его переместили или удалили.",
    # lupa
    "LuaSyntaxError": "В файле ошибка синтаксиса Lua{where}. "
                      "Проверьте его в среде разработки контроллера.",
    "LuaError": "Lua не смог выполнить файл{where}.",
    # общее
    "PermissionError": "Нет доступа к файлу. Возможно, он открыт в другой программе.",
    "MemoryError": "Не хватило памяти. Попробуйте профиль детекции «Быстро».",
}

# Наши собственные сообщения: они уже по-русски и по делу
OUR_ERRORS = (ValueError, IndexError, KeyError)


def _lua_line(text: str) -> str:
    # 'error loading code: [string "<python>"]:88: unfinished string' -> ' (строка 88)'
    match = re.search(r"\]:(\d+):", text)
    return f" (строка {match.group(1)})" if match else ""


def describe(error: BaseException, path: Optional[str] = None) -> str:
    """Объяснение ошибки для человека.

    path — файл, на котором споткнулись: библиотеки вставляют его в текст
    сами, в непригодном виде, а сообщения окна обходятся без него.
    """
    text = str(error)
    known = LIBRARY_MESSAGES.get(type(error).__name__)

    if known:
        message = known.format(where=_lua_line(text))
    elif isinstance(error, OUR_ERRORS) and text and not text.startswith("("):
        # Своё сообщение проходит как есть. Пустой или служебный текст
        # (кортеж аргументов у KeyError) объяснением не является
        message = text.strip()
    else:
        message = f"{type(error).__name__}: {text}" if text else type(error).__name__

    if path:
        import os
        message += f"\n\nФайл: {os.path.basename(path)}"
    return message


# Не ошибка, а пустой результат: чертёж открылся, но рисовать в нём нечего
NO_VECTOR_GRAPHICS = (
    "В файле нет векторной графики — похоже, это скан или изображение.\n\n"
    "Распознавание работает только с векторными чертежами: линии и текст "
    "должны быть объектами, а не точками растра."
)
