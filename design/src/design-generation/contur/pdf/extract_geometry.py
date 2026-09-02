# extract_geometry.py
import fitz
from typing import List, Dict, Tuple, Optional
import math

Point = Tuple[float, float]
Segment = Dict[str, object]


def segment_length(p1: Point, p2: Point) -> float:
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])


def is_dashed(dash_str: str) -> bool:
    return bool(dash_str and dash_str.strip() and '[' in dash_str and dash_str.split(']')[0].replace('[', '').strip())


def _pages(doc, page_number: Optional[int]):
    # page_number=None — все страницы (прежнее поведение),
    # иначе только указанная. Нужно, чтобы геометрия и разметка
    # относились к одной и той же странице многостраничного PDF.
    if page_number is None:
        return doc
    if 0 <= page_number < len(doc):
        return [doc[page_number]]

    # У обрезанного файла страниц ноль, и «нет страницы 0 (всего 0)» звучит
    # как придирка к номеру, хотя дело в самом файле
    if not len(doc):
        raise IndexError("В файле нет ни одной страницы — он повреждён "
                         "или выгрузился не полностью.")
    raise IndexError(f"В PDF нет страницы {page_number + 1} — в файле их {len(doc)}.")


def page_count(pdf_path: str) -> int:
    with fitz.open(pdf_path) as doc:
        return len(doc)


def extract_line_segments(pdf_path: str, page_number: Optional[int] = None) -> List[Segment]:
    segments, doc = [], fitz.open(pdf_path)
    for page in _pages(doc, page_number):
        for d in page.get_drawings():
            dashed = is_dashed(d.get("dashes"))
            for item in d["items"]:
                if item[0] == "l":
                    segments.append({
                        "p1": (item[1].x, item[1].y),
                        "p2": (item[2].x, item[2].y),
                        "dashed": dashed
                    })
    doc.close()
    return segments


def extract_text_elements(pdf_path: str, page_number: Optional[int] = None) -> List[Dict]:
    doc, texts = fitz.open(pdf_path), []
    for page in _pages(doc, page_number):
        for block in page.get_text("dict")["blocks"]:
            if "lines" in block:
                for span in [s for line in block["lines"]
                             for s in line["spans"] if s["text"].strip()]:
                    bbox = span["bbox"]
                    texts.append({
                        "text": span["text"].strip(),
                        "bbox": bbox,
                        "center": ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2),
                        "page": page.number,
                        "font": span["font"],
                        "size": span["size"]
                    })
    doc.close()
    return texts


