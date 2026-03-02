import tkinter as tk
from tkinter import filedialog
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import math
from collections import defaultdict
from typing import List, Dict, Tuple, Any

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


def find_text(contour: ClosedContour, texts: List[Dict]) -> tuple:
    minx, miny, maxx, maxy = contour.bounds
    best = (None, None, float('inf'))

    for t in texts:
        tx, ty = t["center"]
        if minx <= tx <= maxx and miny <= ty <= maxy:
            continue

        dist = min(
            math.hypot(tx - minx, ty - miny), math.hypot(tx - maxx, ty - miny),
            math.hypot(tx - minx, ty - maxy), math.hypot(tx - maxx, ty - maxy),
            abs(tx - minx) if miny <= ty <= maxy else float('inf'),
            abs(tx - maxx) if miny <= ty <= maxy else float('inf'),
            abs(ty - miny) if minx <= tx <= maxx else float('inf'),
            abs(ty - maxy) if minx <= tx <= maxx else float('inf')
        )
        if dist < best[2]:
            best = (t["text"], (tx, ty), dist)

    return best[0], best[1]


def gen_xml(segments: List[SegmentData], contours: List[ClosedContour] = None):
    root = ET.Element("GeometryData")
    segs_el = ET.SubElement(root, "Segments")

    for i, s in enumerate(segments):
        el = ET.SubElement(segs_el, "Segment", id=str(i))
        el.set("x1", f"{s.p1[0]:.3f}");
        el.set("y1", f"{s.p1[1]:.3f}")
        el.set("x2", f"{s.p2[0]:.3f}");
        el.set("y2", f"{s.p2[1]:.3f}")
        el.set("dashed", str(s.dashed))

    if contours:
        c_el = ET.SubElement(root, "ClosedContours")
        for i, c in enumerate(contours):
            el = ET.SubElement(c_el, "Contour", id=str(i))
            ET.SubElement(el, "SegmentRefs").text = " ".join(str(idx) for idx in c.segments)
            b = ET.SubElement(el, "Bounds")
            b.set("min_x", f"{c.bounds[0]:.3f}");
            b.set("min_y", f"{c.bounds[1]:.3f}")
            b.set("max_x", f"{c.bounds[2]:.3f}");
            b.set("max_y", f"{c.bounds[3]:.3f}")
            cent = ET.SubElement(el, "Center")
            cent.set("x", f"{c.center[0]:.3f}");
            cent.set("y", f"{c.center[1]:.3f}")
            if c.name:
                name_el = ET.SubElement(el, "Name")
                name_el.text = c.name
                if c.name_position:
                    name_el.set("pos_x", f"{c.name_position[0]:.3f}")
                    name_el.set("pos_y", f"{c.name_position[1]:.3f}")

    return ET.ElementTree(root)


def visualize(segments: List[SegmentData], contours: List[ClosedContour] = None, texts: List[Dict] = None):
    plt.figure(figsize=(12, 8))
    contour_segs = {i for c in contours or [] for i in c.segments}

    for i, s in enumerate(segments):
        style = ("--", "red", 2) if i in contour_segs else ("--", "black", 0.5) if s.dashed else ("-", "black", 0.3)
        plt.plot([s.p1[0], s.p2[0]], [s.p1[1], s.p2[1]],
                 linestyle=style[0], color=style[1], linewidth=style[2])

    for c in contours or []:
        minx, miny, maxx, maxy = c.bounds
        plt.gca().add_patch(Rectangle((minx, miny), maxx - minx, maxy - miny,
                                      fill=False, edgecolor='blue', linestyle=':'))
        plt.plot(c.center[0], c.center[1], 'ro', markersize=5)
        if c.name:
            plt.text(c.center[0], c.center[1] - 10, c.name, fontsize=8, color='blue',
                     bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

    for t in texts or []:
        plt.plot(t["center"][0], t["center"][1], 'g.', markersize=2)
        plt.text(t["center"][0], t["center"][1] - 2, t["text"], fontsize=6, color='green', alpha=0.7)

    plt.gca().invert_yaxis()
    plt.title("Segments, Contours & Text")
    plt.xlabel("X");
    plt.ylabel("Y");
    plt.grid(True, alpha=0.3)
    plt.tight_layout();
    plt.show()


def main():
    if not (path := choose_pdf()):
        print("Файл не выбран")
        return

    raw = extract_line_segments(path)
    texts = extract_text_elements(path)
    segs = [SegmentData(**s) for s in raw]

    print(f"Сегментов: {len(segs)}, Текстов: {len(texts)}")

    contours = find_contours(segs)
    print(f"Контуров: {len(contours)}")

    for c in contours:
        if name_pos := find_text(c, texts):
            c.name, c.name_position = name_pos
            print(f"Контур -> '{c.name}'")

    gen_xml(segs, contours).write("output.xml", encoding="utf-8", xml_declaration=True)
    visualize(segs, contours, texts)


if __name__ == "__main__":
    main()