# data_models.py
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any
from PySide6.QtGui import QColor


@dataclass
class DeviceOperationState:
    operation_name: str
    state: str
    state_id: Optional[str] = None
    step_name: Optional[str] = None


@dataclass
class DeviceMatch:
    lua_name: str
    pdf_name: str
    tech_object: str
    coordinates: Tuple[float, float]
    confidence: float
    descr: str = ""
    article: str = ""
    device_type: str = ""
    category: str = ""
    extra_data: Dict[str, Any] = field(default_factory=dict)
    operation_states: List[DeviceOperationState] = field(default_factory=list)
    color: Optional[QColor] = None


@dataclass
class Contour:
    name: str
    bounds: Tuple[float, float, float, float]
    center: Tuple[float, float]
    tech_object: str


@dataclass
class Operation:
    id: str
    name: str
    base_operation: Optional[str]
    obj_id: str
    obj_name: str
    props: Dict[str, Any] = field(default_factory=dict)