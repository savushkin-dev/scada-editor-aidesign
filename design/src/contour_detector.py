import tkinter as tk
from tkinter import filedialog
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import math
from collections import defaultdict
from typing import List, Dict, Tuple, Any, Optional

from extract_geometry import extract_line_segments, extract_text_elements
from segment_data import SegmentData, ClosedContour

TOLERANCE, SEARCH_RADIUS = 0.5, 50


def choose_pdf() -> str:
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(title="Выберите PDF", filetypes=[("PDF", "*.pdf")])


def points_equal(p1, p2, tol=TOLERANCE):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1]) < tol


def normalize(p, tol=TOLERANCE):
    return (round(p[0] / tol) * tol, round(p[1] / tol) * tol)


def find_contours(segments: List[SegmentData]) -> List[ClosedContour]:
    graph, visited = defaultdict(list), set()
    for i, s in enumerate(segments):
        if s.dashed:
            p1, p2 = normalize(s.p1), normalize(s.p2)
            graph[p1].append((p2, i))
            graph[p2].append((p1, i))

    contours = []
    for start in graph:
        if start in visited or len(graph[start]) != 2:
            continue

        curr, prev_edge = start, None
        cyc_segs, cyc_nodes = [], []

        while True:
            cyc_nodes.append(curr)
            for nxt, eid in graph[curr]:
                if eid != prev_edge and eid not in visited:
                    visited.add(eid)
                    cyc_segs.append(eid)
                    prev_edge, curr = eid, nxt
                    break
            else:
                break

            if points_equal(curr, start) and len(cyc_segs) >= 3:
                pts = [p for i in cyc_segs for p in [segments[i].p1, segments[i].p2]]
                xs, ys = [p[0] for p in pts], [p[1] for p in pts]
                minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
                contours.append(ClosedContour(
                    segments=cyc_segs,
                    bounds=(minx, miny, maxx, maxy),
                    center=((minx + maxx) / 2, (miny + maxy) / 2)
                ))
                break
    return contours


def parse_text_for_contour_name(text: str) -> Optional[str]:
    # Ищем все части после символа +
    parts = text.split('+')
    if len(parts) > 1:
        # Берем первую часть после + (индекс 1, т.к. часть до + это индекс 0)
        # Убираем пробелы и специальные символы по краям
        candidate = parts[1].strip()

        # Проверяем, что candidate не пустой и не состоит только из спецсимволов
        if candidate and any(c.isalnum() for c in candidate):
            # Возвращаем candidate, убирая возможные спецсимволы в начале/конце
            return candidate.strip('=<>:;,-')
    return None


def point_to_line_distance(point: Tuple[float, float],
                           line_start: Tuple[float, float],
                           line_end: Tuple[float, float]) -> float:
    x0, y0 = point
    x1, y1 = line_start
    x2, y2 = line_end

    # Вычисляем проекцию точки на прямую
    dx = x2 - x1
    dy = y2 - y1

    # Если отрезок вырожден в точку
    if dx == 0 and dy == 0:
        return math.hypot(x0 - x1, y0 - y1)

    # Параметр t для проекции
    t = ((x0 - x1) * dx + (y0 - y1) * dy) / (dx * dx + dy * dy)

    if t < 0:
        # Проекция за пределами отрезка со стороны p1
        return math.hypot(x0 - x1, y0 - y1)
    elif t > 1:
        # Проекция за пределами отрезка со стороны p2
        return math.hypot(x0 - x2, y0 - y2)
    else:
        # Проекция на отрезок
        proj_x = x1 + t * dx
        proj_y = y1 + t * dy
        return math.hypot(x0 - proj_x, y0 - proj_y)


def point_inside_contour(point: Tuple[float, float],
                         contour_segments: List[SegmentData]) -> bool:
    x, y = point
    intersections = 0

    for seg in contour_segments:
        x1, y1 = seg.p1
        x2, y2 = seg.p2

        # Проверяем, пересекает ли горизонтальный луч из точки отрезок
        if ((y1 <= y < y2) or (y2 <= y < y1)):
            # Вычисляем x координату пересечения
            x_intersect = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x_intersect > x:
                intersections += 1

    return intersections % 2 == 1


def find_contour_name_by_proximity(contour: ClosedContour,
                                   segments: List[SegmentData],
                                   texts: List[Dict],
                                   max_distance: float = 100) -> Tuple[
    Optional[str], Optional[Tuple[float, float]], Optional[float]]:
    # Получаем сегменты, принадлежащие контуру
    contour_segments = [segments[i] for i in contour.segments]

    best_match = None
    best_distance = float('inf')
    best_position = None
    best_text = None
    best_is_inside = False

    for t in texts:
        if '+' not in t["text"]:
            continue

        tx, ty = t["center"]
        name = parse_text_for_contour_name(t["text"])
        if not name:
            continue

        # Вычисляем минимальное расстояние от точки до любой линии контура
        min_distance = float('inf')

        for seg in contour_segments:
            dist = point_to_line_distance((tx, ty), seg.p1, seg.p2)
            if dist < min_distance:
                min_distance = dist

        # Проверяем, находится ли точка внутри контура
        is_inside = point_inside_contour((tx, ty), contour_segments)

        # Даем предпочтение точкам внутри контура (они обычно более релевантны)
        # или точкам очень близко к границе
        if is_inside and min_distance < 20:  # Если точка внутри и близко к границе
            min_distance = min_distance * 0.5  # Уменьшаем расстояние, даем приоритет

        if min_distance < best_distance:
            best_distance = min_distance
            best_match = name
            best_position = (tx, ty)
            best_text = t["text"]
            best_is_inside = is_inside

    # Если нашли текст достаточно близко к линиям контура
    if best_match and best_distance <= max_distance:
        inside_outside = "внутри" if best_is_inside else "снаружи"
        print(f"    Найден текст '{best_text}' на расстоянии {best_distance:.1f} от линий контура ({inside_outside})")
        return best_match, best_position, best_distance

    return None, None, None


def find_all_contour_names_by_proximity(contours: List[ClosedContour],
                                        segments: List[SegmentData],
                                        texts: List[Dict],
                                        max_distance: float = 150) -> None:

    # Сортируем контуры по площади (меньшие обычно имеют более точные имена)
    sorted_contours = sorted(contours, key=lambda c:
    (c.bounds[2] - c.bounds[0]) * (c.bounds[3] - c.bounds[1]))

    used_texts = set()  # для предотвращения дублирования

    print("\n" + "=" * 60)
    print("ПОИСК ИМЕН КОНТУРОВ")
    print("=" * 60)

    for i, contour in enumerate(sorted_contours):
        print(f"\nКонтур {i + 1} (центр: ({contour.center[0]:.1f}, {contour.center[1]:.1f}), "
              f"размер: {(contour.bounds[2] - contour.bounds[0]):.1f} x {(contour.bounds[3] - contour.bounds[1]):.1f}):")

        # Находим все тексты с +, которые еще не использованы
        candidates = []

        for j, t in enumerate(texts):
            if j in used_texts or '+' not in t["text"]:
                continue

            tx, ty = t["center"]
            name = parse_text_for_contour_name(t["text"])
            if not name:
                continue

            # Вычисляем расстояние до линий контура
            contour_segments = [segments[k] for k in contour.segments]
            min_distance = float('inf')

            for seg in contour_segments:
                dist = point_to_line_distance((tx, ty), seg.p1, seg.p2)
                if dist < min_distance:
                    min_distance = dist

            # Проверяем, внутри ли контура
            is_inside = point_inside_contour((tx, ty), contour_segments)

            if min_distance <= max_distance:
                candidates.append({
                    'text_idx': j,
                    'name': name,
                    'position': (tx, ty),
                    'distance': min_distance,
                    'full_text': t["text"],
                    'is_inside': is_inside
                })

        # Сортируем кандидатов по расстоянию (с приоритетом для внутренних)
        candidates.sort(key=lambda x: (x['distance'] * (0.5 if x['is_inside'] else 1.0)))

        if candidates:
            # Берем ближайший
            best = candidates[0]
            contour.name = best['name']
            contour.name_position = best['position']
            used_texts.add(best['text_idx'])

            location = "ВНУТРИ" if best['is_inside'] else "СНАРУЖИ"
            print(f"  ✓ НАЗНАЧЕНО: '{contour.name}' от текста '{best['full_text']}'")
            print(f"    Расстояние до линии: {best['distance']:.1f}, {location}")

            # Показываем других кандидатов для отладки
            if len(candidates) > 1:
                print(f"    Другие кандидаты:")
                for c in candidates[1:4]:  # показываем до 3 дополнительных
                    loc = "внутри" if c['is_inside'] else "снаружи"
                    print(f"      '{c['full_text']}' -> '{c['name']}' - {c['distance']:.1f} ({loc})")
        else:
            print(f"  ✗ Нет подходящего текста с + в пределах {max_distance}")


def gen_xml(segments: List[SegmentData], contours: List[ClosedContour] = None):
    root = ET.Element("GeometryData")
    segs_el = ET.SubElement(root, "Segments")

    for i, s in enumerate(segments):
        el = ET.SubElement(segs_el, "Segment", id=str(i))
        el.set("x1", f"{s.p1[0]:.3f}")
        el.set("y1", f"{s.p1[1]:.3f}")
        el.set("x2", f"{s.p2[0]:.3f}")
        el.set("y2", f"{s.p2[1]:.3f}")
        el.set("dashed", str(s.dashed))

    if contours:
        c_el = ET.SubElement(root, "ClosedContours")
        for i, c in enumerate(contours):
            el = ET.SubElement(c_el, "Contour", id=str(i))
            ET.SubElement(el, "SegmentRefs").text = " ".join(str(idx) for idx in c.segments)
            b = ET.SubElement(el, "Bounds")
            b.set("min_x", f"{c.bounds[0]:.3f}")
            b.set("min_y", f"{c.bounds[1]:.3f}")
            b.set("max_x", f"{c.bounds[2]:.3f}")
            b.set("max_y", f"{c.bounds[3]:.3f}")
            cent = ET.SubElement(el, "Center")
            cent.set("x", f"{c.center[0]:.3f}")
            cent.set("y", f"{c.center[1]:.3f}")
            if c.name:
                name_el = ET.SubElement(el, "Name")
                name_el.text = c.name
                if c.name_position:
                    name_el.set("pos_x", f"{c.name_position[0]:.3f}")
                    name_el.set("pos_y", f"{c.name_position[1]:.3f}")

    return ET.ElementTree(root)


def visualize(segments: List[SegmentData], contours: List[ClosedContour] = None, texts: List[Dict] = None):
    plt.figure(figsize=(16, 12))
    contour_segs = {i for c in contours or [] for i in c.segments}

    # Рисуем все сегменты
    for i, s in enumerate(segments):
        if i in contour_segs:
            # Сегменты контура рисуем жирнее
            plt.plot([s.p1[0], s.p2[0]], [s.p1[1], s.p2[1]],
                     linestyle='-', color='blue', linewidth=2, alpha=0.6)
        else:
            style = ("--", "black", 0.5) if s.dashed else ("-", "gray", 0.3)
            plt.plot([s.p1[0], s.p2[0]], [s.p1[1], s.p2[1]],
                     linestyle=style[0], color=style[1], linewidth=style[2])

    # Рисуем контуры и их имена
    for c in contours or []:
        # Центр контура (маленькая точка)
        plt.plot(c.center[0], c.center[1], 'bo', markersize=4)

        # Имя контура
        if c.name and c.name_position:
            # Рисуем линию от имени до ближайшей точки контура
            # Находим ближайшую точку на контуре
            contour_segments_list = [segments[i] for i in c.segments]
            min_dist = float('inf')
            closest_point = None

            for seg in contour_segments_list:
                # Проверяем начальную точку
                d1 = math.hypot(c.name_position[0] - seg.p1[0],
                                c.name_position[1] - seg.p1[1])
                if d1 < min_dist:
                    min_dist = d1
                    closest_point = seg.p1

                # Проверяем конечную точку
                d2 = math.hypot(c.name_position[0] - seg.p2[0],
                                c.name_position[1] - seg.p2[1])
                if d2 < min_dist:
                    min_dist = d2
                    closest_point = seg.p2

            if closest_point:
                plt.plot([c.name_position[0], closest_point[0]],
                         [c.name_position[1], closest_point[1]],
                         'g--', linewidth=0.8, alpha=0.5)

            # Текст имени
            plt.text(c.name_position[0], c.name_position[1] - 8,
                     f"  {c.name}", fontsize=10, color='darkred', weight='bold',
                     bbox=dict(facecolor='yellow', alpha=0.8, edgecolor='red', pad=2))

        # Рисуем bounding box пунктиром
        minx, miny, maxx, maxy = c.bounds
        plt.gca().add_patch(Rectangle((minx, miny), maxx - minx, maxy - miny,
                                      fill=False, edgecolor='blue', linestyle=':', linewidth=1))

    # Рисуем текстовые элементы
    for t in texts or []:
        if '+' in t["text"]:
            # Тексты с + выделяем
            plt.plot(t["center"][0], t["center"][1], 'r*', markersize=8, markeredgecolor='darkred')
            plt.text(t["center"][0], t["center"][1] - 12, t["text"],
                     fontsize=8, color='darkred', weight='bold',
                     bbox=dict(facecolor='lightyellow', alpha=0.7, edgecolor='red', pad=1))
        else:
            plt.plot(t["center"][0], t["center"][1], 'g.', markersize=3)
            plt.text(t["center"][0], t["center"][1] - 4, t["text"],
                     fontsize=6, color='green', alpha=0.6)

    plt.gca().invert_yaxis()
    plt.title("Анализ чертежа: контуры (синий), имена контуров (красный), текст с + (звездочки)", fontsize=14)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def main():
    if not (path := choose_pdf()):
        print("Файл не выбран")
        return

    print(f"Обработка файла: {path}")

    raw = extract_line_segments(path)
    texts = extract_text_elements(path)
    segs = [SegmentData(**s) for s in raw]

    print(f"\nСегментов: {len(segs)}")
    print(f"Текстов: {len(texts)}")

    # Анализируем тексты с +
    plus_texts = [t for t in texts if '+' in t["text"]]
    if plus_texts:
        print(f"\nНайдено текстов с символом '+': {len(plus_texts)}")
        for i, t in enumerate(plus_texts):
            parsed = parse_text_for_contour_name(t["text"])
            print(f"  {i + 1}. '{t['text']}' -> '{parsed}' в позиции ({t['center'][0]:.1f}, {t['center'][1]:.1f})")
    else:
        print("\n❌ Тексты с символом '+' не найдены!")
        return

    contours = find_contours(segs)
    print(f"\nНайдено замкнутых контуров: {len(contours)}")

    if not contours:
        print("❌ Контуры не найдены!")
        return

    # Находим имена для контуров на основе расстояния до линий
    find_all_contour_names_by_proximity(contours, segs, texts, max_distance=200)

    # Подсчитываем статистику
    named_contours = [c for c in contours if c.name]
    print(f"\n{'=' * 60}")
    print(f"ИТОГ: именовано контуров: {len(named_contours)} из {len(contours)}")
    print(f"{'=' * 60}")

    # Сохраняем результаты
    xml_file = "output.xml"
    gen_xml(segs, contours).write(xml_file, encoding="utf-8", xml_declaration=True)
    print(f"\nРезультаты сохранены в {xml_file}")

    # Визуализируем
    print("\nОткрытие визуализации...")
    visualize(segs, contours, texts)


if __name__ == "__main__":
    main()