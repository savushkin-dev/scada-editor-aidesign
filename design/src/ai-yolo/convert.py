import fitz
import os
from pathlib import Path

# Настройки
PDF_PATH = "D:/PYTHON PROJECTS/CONTUR/input/test1/BN1-МОЛОКОХРАНИЛИЩЕ-2025Full-4.pdf"
OUTPUT_DIR = "images_for_labeling"
DPI = 600  # высокое разрешение для четкой разметки

# Создаем папку, если её нет
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"📄 Конвертируем PDF в PNG для LabelImg...")
print(f"   Файл: {PDF_PATH}")
print(f"   Папка: {OUTPUT_DIR}")
print(f"   DPI: {DPI}")
print("-" * 50)

try:
    # Открываем PDF
    doc = fitz.open(PDF_PATH)
    total_pages = len(doc)
    print(f"📊 Всего страниц в PDF: {total_pages}")

    for page_num in range(total_pages):
        page = doc[page_num]

        # Конвертируем в изображение
        zoom = DPI / 72
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)

        # Сохраняем
        output_path = f"{OUTPUT_DIR}/page_{page_num + 1:03d}.png"
        pix.save(output_path)
        print(f"✅ [{page_num + 1}/{total_pages}] Сохранено: {output_path}")

    print("-" * 50)
    print(f"✅ Успешно конвертировано {total_pages} страниц в {OUTPUT_DIR}")

except Exception as e:
    print(f"❌ Ошибка: {e}")

finally:
    # Закрываем документ только после завершения всех операций
    if 'doc' in locals():
        doc.close()
        print("📌 Документ закрыт")