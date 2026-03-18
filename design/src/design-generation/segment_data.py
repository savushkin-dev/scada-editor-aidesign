from dataclasses import dataclass
from typing import Tuple, List, Optional

Point = Tuple[float, float]

@dataclass
class SegmentData:
    p1: Point
    p2: Point
    dashed: bool = False

@dataclass
class ClosedContour:
    segments: List[int]
    bounds: Tuple[float, float, float, float]
    center: Point
    name: Optional[str] = None
    name_position: Optional[Point] = None