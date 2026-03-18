import os
import glob
import cv2
import torch
import random
import xml.etree.ElementTree as ET
from ultralytics import YOLO

import multiprocessing
multiprocessing.freeze_support()


def main():

    XML_DIR = "output"
    IMG_DIR = "images_for_labeling"
    DATASET = "dataset"

    TILE = 1024
    OVERLAP = 256

    TRAIN_SPLIT = 0.8

    CLASSES = {
        "valve": 0,
        "valve1": 0,
        "valve2": 0,
        "valve3": 0,
        "sensor": 1,
        "pump": 2
    }


    if torch.cuda.is_available():
        device = 0
        print("CUDA:", torch.cuda.get_device_name(0))
    else:
        device = "cpu"
        print("CPU mode")


    for p in [
        "images/train",
        "images/val",
        "labels/train",
        "labels/val"
    ]:
        os.makedirs(f"{DATASET}/{p}", exist_ok=True)

    # XML парсер

    def read_xml(xml_path):

        tree = ET.parse(xml_path)
        root = tree.getroot()

        boxes = []

        for obj in root.findall("object"):

            name = obj.find("name").text

            if name not in CLASSES:
                continue

            cls = CLASSES[name]

            b = obj.find("bndbox")

            xmin = int(b.find("xmin").text)
            ymin = int(b.find("ymin").text)
            xmax = int(b.find("xmax").text)
            ymax = int(b.find("ymax").text)

            boxes.append([cls, xmin, ymin, xmax, ymax])

        return boxes


    # Tile img

    def tile_image(img, boxes, name, subset):

        H, W = img.shape[:2]
        tile_id = 0

        step = TILE - OVERLAP

        for y in range(0, H - TILE, step):
            for x in range(0, W - TILE, step):

                crop = img[y:y+TILE, x:x+TILE]

                labels = []

                for cls, x1, y1, x2, y2 in boxes:

                    ix1 = max(x1, x)
                    iy1 = max(y1, y)
                    ix2 = min(x2, x + TILE)
                    iy2 = min(y2, y + TILE)

                    if ix1 >= ix2 or iy1 >= iy2:
                        continue

                    ix1 -= x
                    iy1 -= y
                    ix2 -= x
                    iy2 -= y

                    bw = (ix2 - ix1) / TILE
                    bh = (iy2 - iy1) / TILE
                    cx = (ix1 + ix2) / 2 / TILE
                    cy = (iy1 + iy2) / 2 / TILE

                    labels.append([cls, cx, cy, bw, bh])

                if not labels:
                    continue

                tile_name = f"{name}_{tile_id}"

                cv2.imwrite(
                    f"{DATASET}/images/{subset}/{tile_name}.png",
                    crop
                )

                with open(
                    f"{DATASET}/labels/{subset}/{tile_name}.txt", "w"
                ) as f:
                    for l in labels:
                        f.write(" ".join(map(str, l)) + "\n")

                tile_id += 1


    # Построение датасета

    xml_files = glob.glob(f"{XML_DIR}/*.xml")
    random.shuffle(xml_files)

    split = int(len(xml_files) * TRAIN_SPLIT)

    train_files = xml_files[:split]
    val_files = xml_files[split:]

    print("Train:", len(train_files))
    print("Val:", len(val_files))

    for xml_path in train_files:

        name = os.path.basename(xml_path).replace(".xml", "")
        img_path = f"{IMG_DIR}/{name}.png"

        if not os.path.exists(img_path):
            continue

        img = cv2.imread(img_path)
        boxes = read_xml(xml_path)

        tile_image(img, boxes, name, "train")

    for xml_path in val_files:

        name = os.path.basename(xml_path).replace(".xml", "")
        img_path = f"{IMG_DIR}/{name}.png"

        if not os.path.exists(img_path):
            continue

        img = cv2.imread(img_path)
        boxes = read_xml(xml_path)

        tile_image(img, boxes, name, "val")


    # YAML

    yaml = f"""
path: {DATASET}

train: images/train
val: images/val

names:
  0: valve
  1: sensor
  2: pump
"""

    with open("dataset.yaml", "w") as f:
        f.write(yaml)


    # Обучение

    model = YOLO("yolov8n.pt")

    model.train(
        data="dataset.yaml",
        epochs=200,
        imgsz=TILE,
        batch=4,
        device=device,
        workers=0,
        cache=False
    )


if __name__ == "__main__":
    main()
