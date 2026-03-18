import fitz
import svgwrite
from ultralytics import YOLO
import cv2
import numpy as np

MODEL = "runs/detect/train2/weights/best.pt"
PDF_PATH = "D:/PYTHON PROJECTS/CONTUR/input/test1/BN1-МОЛОКОХРАНИЛИЩЕ-2025Full-4.pdf"
PNG_PATH = "images_for_labeling/test/BN1-МОЛОКОХРАНИЛИЩЕ-2025Full-4.png"

TILE = 1024
CONF = 0.25
STEP = 768

print("Шаг 1: Обнаружение устройств на PNG...")

model = YOLO(MODEL)

img = cv2.imread(PNG_PATH)
if img is None:
    print("Ошибка загрузки PNG")
    exit(1)

H, W = img.shape[:2]
print(f"Размер PNG: {W}x{H}")

device_rectangles = []

for y in range(0, H - TILE, STEP):
    for x in range(0, W - TILE, STEP):

        tile = img[y:y+TILE, x:x+TILE]

        if tile.shape[0] < TILE or tile.shape[1] < TILE:
            continue

        results = model.predict(tile, conf=CONF, imgsz=TILE, verbose=False)

        for r in results:
            boxes = r.boxes.xyxy.cpu().numpy()

            for box in boxes:
                x1, y1, x2, y2 = box

                x1_abs = int(x1) + x
                x2_abs = int(x2) + x
                y1_abs = int(y1) + y
                y2_abs = int(y2) + y

                device_rectangles.append((x1_abs, y1_abs, x2_abs, y2_abs))

print(f"Найдено устройств: {len(device_rectangles)}")

print("Шаг 2: Обработка PDF...")

pdf_document = fitz.open(PDF_PATH)
page = pdf_document[0]

pdf_rect = page.rect
pdf_width = pdf_rect.width
pdf_height = pdf_rect.height

print(f"Размер PDF: {pdf_width} x {pdf_height}")

scale_x = pdf_width / W
scale_y = pdf_height / H

device_rectangles_pdf = []

for x1, y1, x2, y2 in device_rectangles:

    device_rectangles_pdf.append((
        x1 * scale_x,
        y1 * scale_y,
        x2 * scale_x,
        y2 * scale_y
    ))

device_rectangles = device_rectangles_pdf

dwg = svgwrite.Drawing(
    "result_vector.svg",
    size=(f"{pdf_width}pt", f"{pdf_height}pt"),
    profile="full"
)

dwg.add(
    dwg.rect(
        insert=(0, 0),
        size=(f"{pdf_width}pt", f"{pdf_height}pt"),
        fill="white"
    )
)

def safe_float(v, default=1.0):
    try:
        return float(v)
    except:
        return default


def point_in_device(x, y, rects, tolerance=5):

    for x1, y1, x2, y2 in rects:

        if (
            x1 - tolerance <= x <= x2 + tolerance and
            y1 - tolerance <= y <= y2 + tolerance
        ):
            return True

    return False


def line_in_device(x1, y1, x2, y2, rects, tolerance=3):

    # центр линии
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2

    for rx1, ry1, rx2, ry2 in rects:

        if (
            rx1 - tolerance <= cx <= rx2 + tolerance and
            ry1 - tolerance <= cy <= ry2 + tolerance
        ):
            return True

    return False


print("Шаг 3: Извлечение графики...")

paths = page.get_drawings()

device_count = 0
pipe_count = 0
other_count = 0

for path in paths:

    items = path.get("items", [])
    stroke_width = safe_float(path.get("width"), 1.0)

    for item in items:

        try:

            if item[0] == "l":

                _, p1, p2 = item
                x1, y1 = p1
                x2, y2 = p2

                if line_in_device(x1, y1, x2, y2, device_rectangles):

                    color = "red"
                    device_count += 1

                else:

                    color = "blue"
                    pipe_count += 1

                dwg.add(
                    dwg.line(
                        start=(x1, y1),
                        end=(x2, y2),
                        stroke=color,
                        stroke_width=stroke_width
                    )
                )

            elif item[0] == "re":

                _, rect = item
                x, y, w, h = rect

                cx = x + w/2
                cy = y + h/2

                if point_in_device(cx, cy, device_rectangles):

                    color = "red"
                    device_count += 1

                else:

                    color = "blue"
                    pipe_count += 1

                dwg.add(
                    dwg.rect(
                        insert=(x, y),
                        size=(w, h),
                        fill="none",
                        stroke=color,
                        stroke_width=stroke_width
                    )
                )

            elif item[0] == "c":

                _, p1, p2, p3, p4 = item

                points = [p1, p2, p3, p4]

                is_device = False

                for px, py in points:
                    if point_in_device(px, py, device_rectangles):
                        is_device = True
                        break

                if is_device:
                    color = "red"
                    device_count += 1
                else:
                    color = "blue"
                    pipe_count += 1

                path_data = f"M {p1[0]},{p1[1]} C {p2[0]},{p2[1]} {p3[0]},{p3[1]} {p4[0]},{p4[1]}"

                dwg.add(
                    dwg.path(
                        d=path_data,
                        fill="none",
                        stroke=color,
                        stroke_width=stroke_width
                    )
                )

            else:

                other_count += 1

        except Exception as e:

            print("Ошибка:", e)


print("Шаг 4: Добавление текста...")

text_data = page.get_text("dict")

for block in text_data["blocks"]:

    if "lines" not in block:
        continue

    for line in block["lines"]:

        for span in line["spans"]:

            text = span["text"]
            size = span["size"]
            bbox = span["bbox"]

            x = bbox[0]
            y = bbox[1]

            if point_in_device(x, y, device_rectangles):
                color = "red"
            else:
                color = "blue"

            dwg.add(
                dwg.text(
                    text,
                    insert=(x, y),
                    fill=color,
                    font_size=size
                )
            )

dwg.save()

print("SVG сохранён")

print("Статистика:")
print("устройства:", device_count)
print("трубы:", pipe_count)

print("Создание проверочного PNG...")

zoom = 2
mat = fitz.Matrix(zoom, zoom)
pix = page.get_pixmap(matrix=mat)

img_data = np.frombuffer(
    pix.samples,
    dtype=np.uint8
).reshape(pix.height, pix.width, 3)

img_data = cv2.cvtColor(img_data, cv2.COLOR_RGB2BGR)

for x1, y1, x2, y2 in device_rectangles:

    cv2.rectangle(
        img_data,
        (int(x1 * zoom), int(y1 * zoom)),
        (int(x2 * zoom), int(y2 * zoom)),
        (0, 0, 255),
        2
    )

cv2.imwrite("result_check.png", img_data)

pdf_document.close()

print("Готово!")