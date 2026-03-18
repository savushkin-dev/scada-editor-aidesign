import tkinter as tk
from tkinter import filedialog
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import math
from collections import defaultdict
from typing import List, Dict, Tuple, Optional
import json
import os

from extract_geometry import extract_line_segments, extract_text_elements
from segment_data import SegmentData, ClosedContour


TOLERANCE = 0.5
LUA_JSON_PATH = "output/parsed_lua_objects.json"


# =========================
# LUA DATA
# =========================

def load_lua_data():
    try:
        if os.path.exists(LUA_JSON_PATH):
            with open(LUA_JSON_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ Lua объектов: {len(data.get('tech_objects', []))}")
            return data
    except Exception as e:
        print("Lua load error:", e)

    return {}


def extract_lua_names(lua_data):

    result = {}

    for obj in lua_data.get("tech_objects", []):

        name_eplan = obj.get("name_eplan", "")
        name_bc = obj.get("name_BC", "")

        if name_eplan:
            result[name_eplan.upper()] = obj

        if name_bc and name_bc != name_eplan:
            result[name_bc.upper()] = obj

    return result


def find_best_lua_match(candidate, lua_names):

    if not candidate:
        return None

    key = candidate.upper()

    if key in lua_names:
        return lua_names[key]

    # TANK1 → TANK
    if key.startswith("TANK"):
        if "TANK" in lua_names:
            obj = lua_names["TANK"].copy()
            obj["tank_number"] = key.replace("TANK", "")
            return obj

    # M1 → M
    if key.startswith("M") and key[1:].isdigit():
        if "M" in lua_names:
            obj = lua_names["M"].copy()
            obj["motor_number"] = key.replace("M", "")
            return obj

    return None


# =========================
# UTILS
# =========================

def choose_pdf():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])


def normalize(p):
    return (round(p[0] / TOLERANCE) * TOLERANCE,
            round(p[1] / TOLERANCE) * TOLERANCE)


def points_equal(p1, p2):
    return math.hypot(p1[0]-p2[0], p1[1]-p2[1]) < TOLERANCE


def parse_text_for_contour_name(text):

    parts = text.split('+')

    if len(parts) > 1:

        candidate = parts[1].strip()

        if candidate and any(c.isalnum() for c in candidate):
            return candidate.strip('=<>:;,-')

    return None


# Геометрия

def point_to_line_distance(p, a, b):

    x0,y0 = p
    x1,y1 = a
    x2,y2 = b

    dx = x2-x1
    dy = y2-y1

    if dx==0 and dy==0:
        return math.hypot(x0-x1,y0-y1)

    t = ((x0-x1)*dx+(y0-y1)*dy)/(dx*dx+dy*dy)

    if t<0:
        return math.hypot(x0-x1,y0-y1)
    elif t>1:
        return math.hypot(x0-x2,y0-y2)

    projx=x1+t*dx
    projy=y1+t*dy

    return math.hypot(x0-projx,y0-projy)


def point_inside_contour(point, contour_segments):

    x,y = point
    intersections=0

    for seg in contour_segments:

        x1,y1=seg.p1
        x2,y2=seg.p2

        if ((y1<=y<y2) or (y2<=y<y1)):

            x_int = x1 + (y-y1)*(x2-x1)/(y2-y1)

            if x_int > x:
                intersections+=1

    return intersections%2==1


# Распознавание контуров

def find_contours(segments):

    graph=defaultdict(list)
    visited=set()

    for i,s in enumerate(segments):

        if s.dashed:

            p1=normalize(s.p1)
            p2=normalize(s.p2)

            graph[p1].append((p2,i))
            graph[p2].append((p1,i))

    contours=[]

    for start in graph:

        if start in visited or len(graph[start])!=2:
            continue

        curr=start
        prev=None

        cyc=[]

        while True:

            for nxt,eid in graph[curr]:

                if eid!=prev and eid not in visited:

                    visited.add(eid)
                    cyc.append(eid)

                    prev=eid
                    curr=nxt
                    break
            else:
                break

            if points_equal(curr,start) and len(cyc)>=3:

                pts=[p for i in cyc for p in [segments[i].p1,segments[i].p2]]

                xs=[p[0] for p in pts]
                ys=[p[1] for p in pts]

                minx,maxx=min(xs),max(xs)
                miny,maxy=min(ys),max(ys)

                contours.append(
                    ClosedContour(
                        segments=cyc,
                        bounds=(minx,miny,maxx,maxy),
                        center=((minx+maxx)/2,(miny+maxy)/2)
                    )
                )

                break

    return contours



# Сопоставление контуров

def find_all_contour_names_by_proximity(contours,
                                        segments,
                                        texts,
                                        lua_names=None,
                                        max_distance=150):

    sorted_contours = sorted(
        contours,
        key=lambda c:(c.bounds[2]-c.bounds[0])*(c.bounds[3]-c.bounds[1])
    )

    used_texts=set()

    print("\nПОИСК ИМЕН КОНТУРОВ (Lua приоритет)")

    for contour in sorted_contours:

        contour_segments=[segments[i] for i in contour.segments]

        candidates=[]

        for j,t in enumerate(texts):

            if j in used_texts:
                continue

            if '+' not in t["text"]:
                continue

            name=parse_text_for_contour_name(t["text"])

            if not name:
                continue

            tx,ty=t["center"]

            min_dist=min(
                point_to_line_distance((tx,ty),seg.p1,seg.p2)
                for seg in contour_segments
            )

            if min_dist>max_distance:
                continue

            inside=point_inside_contour((tx,ty),contour_segments)

            lua_match=None
            if lua_names:
                lua_match=find_best_lua_match(name,lua_names)

            score=min_dist

            if lua_match and inside:
                score*=0.1
            elif lua_match:
                score*=0.3
            elif inside:
                score*=0.8

            candidates.append(
                dict(
                    idx=j,
                    name=name,
                    lua=lua_match,
                    pos=(tx,ty),
                    dist=min_dist,
                    score=score,
                    inside=inside
                )
            )

        if not candidates:
            continue

        candidates.sort(key=lambda x:x["score"])

        best=candidates[0]

        final_name=best["name"]

        if best["lua"]:

            lua_obj=best["lua"]

            if "tank_number" in lua_obj:
                final_name=f"TANK{lua_obj['tank_number']}"

            elif "motor_number" in lua_obj:
                final_name=f"M{lua_obj['motor_number']}"

            else:
                final_name=lua_obj.get("name_eplan",final_name)

        contour.name=final_name
        contour.name_position=best["pos"]
        contour.original_name=best["name"]

        used_texts.add(best["idx"])

        print(f"✓ {best['name']} -> {final_name}")


# XML (Старый формат)

def gen_xml(segments, contours):

    root=ET.Element("GeometryData")

    segs_el=ET.SubElement(root,"Segments")

    for i,s in enumerate(segments):

        el=ET.SubElement(segs_el,"Segment",id=str(i))

        el.set("x1",f"{s.p1[0]:.3f}")
        el.set("y1",f"{s.p1[1]:.3f}")
        el.set("x2",f"{s.p2[0]:.3f}")
        el.set("y2",f"{s.p2[1]:.3f}")
        el.set("dashed",str(s.dashed))

    c_el=ET.SubElement(root,"ClosedContours")

    for i,c in enumerate(contours):

        if not c.name:
            continue

        el=ET.SubElement(c_el,"Contour",id=str(i))

        ET.SubElement(el,"SegmentRefs").text=" ".join(map(str,c.segments))

        b=ET.SubElement(el,"Bounds")

        b.set("min_x",f"{c.bounds[0]:.3f}")
        b.set("min_y",f"{c.bounds[1]:.3f}")
        b.set("max_x",f"{c.bounds[2]:.3f}")
        b.set("max_y",f"{c.bounds[3]:.3f}")

        cent=ET.SubElement(el,"Center")

        cent.set("x",f"{c.center[0]:.3f}")
        cent.set("y",f"{c.center[1]:.3f}")

        name_el=ET.SubElement(el,"Name")
        name_el.text=c.name

        if c.name_position:
            name_el.set("pos_x",f"{c.name_position[0]:.3f}")
            name_el.set("pos_y",f"{c.name_position[1]:.3f}")

    return ET.ElementTree(root)



def main():

    path=choose_pdf()

    if not path:
        return

    print("PDF:",path)

    lua_data=load_lua_data()
    lua_names=extract_lua_names(lua_data) if lua_data else {}

    raw=extract_line_segments(path)
    texts=extract_text_elements(path)

    segments=[SegmentData(**s) for s in raw]

    contours=find_contours(segments)

    print("Контуров:",len(contours))

    find_all_contour_names_by_proximity(
        contours,
        segments,
        texts,
        lua_names,
        max_distance=200
    )

    gen_xml(segments,contours).write(
        "output.xml",
        encoding="utf-8",
        xml_declaration=True
    )

    print("XML сохранён")


if __name__=="__main__":
    main()