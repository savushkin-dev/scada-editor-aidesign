# extract_geometry.py
import fitz
from typing import List, Dict, Tuple
import math
import xml.etree.ElementTree as ET

Point = Tuple[float, float]
Segment = Dict[str, object]


def segment_length(p1: Point, p2: Point) -> float:
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])


def is_dashed(dash_str: str) -> bool:
    return bool(dash_str and dash_str.strip() and '[' in dash_str and dash_str.split(']')[0].replace('[', '').strip())


def extract_line_segments(pdf_path: str) -> List[Segment]:
    segments, doc = [], fitz.open(pdf_path)
    for page in doc:
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


def extract_text_elements(pdf_path: str) -> List[Dict]:
    doc, texts = fitz.open(pdf_path), []
    for page in doc:
        for block in page.get_text("dict")["blocks"]:
            if "lines" in block:
                for span in [s for l in block["lines"] for s in l["spans"] if s["text"].strip()]:
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


def save_texts_to_xml(texts: List[Dict], output_path: str = "output/texts.xml"):
    root = ET.Element("TextElements")

    for i, text in enumerate(texts):
        text_elem = ET.SubElement(root, "Text", id=str(i))
        text_elem.set("content", text["text"])
        text_elem.set("x", f"{text['center'][0]:.3f}")
        text_elem.set("y", f"{text['center'][1]:.3f}")
        text_elem.set("page", str(text["page"]))

        bbox = ET.SubElement(text_elem, "BBox")
        bbox.set("x1", f"{text['bbox'][0]:.3f}")
        bbox.set("y1", f"{text['bbox'][1]:.3f}")
        bbox.set("x2", f"{text['bbox'][2]:.3f}")
        bbox.set("y2", f"{text['bbox'][3]:.3f}")

    tree = ET.ElementTree(root)
    tree.write(output_path, encoding="utf-8", xml_declaration=True)