# objects_loader.py (исправленная версия)
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Parameter:
    id: str
    name: str
    value: Any
    meter: str
    nameLua: str
    oper: List[int]


@dataclass
class Step:
    id: str
    name: str
    step_number: int
    state_id: str
    operation_id: str
    operation_name: str
    obj_id: str
    obj_name: str
    time_param_n: int = -1
    next_step_n: int = -1
    baseStep: Optional[str] = None
    opened_devices: List[str] = field(default_factory=list)
    closed_devices: List[str] = field(default_factory=list)
    devices_data: List[Dict] = field(default_factory=list)
    di_do: List[List] = field(default_factory=list)
    enable_step_by_signal: Optional[List] = None
    jump_if: Optional[List] = None


@dataclass
class State:
    id: str
    name: str
    operation_id: str
    operation_name: str
    obj_id: str
    obj_name: str
    state_data: Dict[str, Any] = field(default_factory=dict)
    steps: List[Step] = field(default_factory=list)


@dataclass
class Operation:
    id: str
    name: str
    base_operation: Optional[str]
    obj_id: str
    obj_name: str
    props: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TechObject:
    id: str
    n: int
    tech_type: int
    name: str
    name_eplan: str
    name_BC: str
    base_tech_object: str
    attached_objects: Optional[str]
    cooper_param_number: int
    parameters: List[Parameter] = field(default_factory=list)
    system_parameters: Dict[str, Any] = field(default_factory=dict)
    properties: Dict[str, str] = field(default_factory=dict)
    equipment: Dict[str, str] = field(default_factory=dict)
    operations: List[Operation] = field(default_factory=list)


class ObjectsData:
    def __init__(self):
        self.objects: List[TechObject] = []
        self.operations: List[Operation] = []
        self.states: List[State] = []
        self.steps: List[Step] = []
        self.parameters: List[Parameter] = []

        # Словари для быстрого доступа
        self.objects_by_id: Dict[str, TechObject] = {}
        self.operations_by_id: Dict[str, Operation] = {}
        self.operations_by_obj_id: Dict[str, List[Operation]] = {}
        self.states_by_operation_id: Dict[str, List[State]] = {}
        self.steps_by_state_id: Dict[str, List[Step]] = {}
        self.parameters_by_obj_id: Dict[str, List[Parameter]] = {}

    def load(self, file_path: str = "output/parsed_lua_objects.json") -> bool:
        try:
            if not Path(file_path).exists():
                print(f"❌ Файл не найден: {file_path}")
                return False

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Очищаем текущие данные
            self._clear()

            # Сначала загружаем все операции из общего списка
            all_operations = []
            for op_data in data.get("operations", []):
                operation = Operation(
                    id=op_data.get("id", ""),
                    name=op_data.get("name", ""),
                    base_operation=op_data.get("base_operation"),
                    obj_id=op_data.get("obj_id", ""),
                    obj_name=op_data.get("obj_name", ""),
                    props=op_data.get("props", {})
                )
                all_operations.append(operation)
                self.operations.append(operation)
                self.operations_by_id[operation.id] = operation

            print(f"  Загружено операций из общего списка: {len(all_operations)}")

            # Загружаем технологические объекты
            for obj_data in data.get("tech_objects", []):
                tech_obj = self._parse_tech_object(obj_data)

                # Находим операции, принадлежащие этому объекту
                obj_operations = []
                for op in all_operations:
                    if op.obj_id == tech_obj.id:
                        obj_operations.append(op)

                # Присваиваем операции объекту
                tech_obj.operations = obj_operations

                self.objects.append(tech_obj)
                self.objects_by_id[tech_obj.id] = tech_obj
                self.operations_by_obj_id[tech_obj.id] = obj_operations

                # Загружаем параметры объекта
                obj_parameters = []
                for param_data in obj_data.get("parameters", []):
                    param = Parameter(
                        id=param_data.get("id", ""),
                        name=param_data.get("name", ""),
                        value=param_data.get("value", 0),
                        meter=param_data.get("meter", ""),
                        nameLua=param_data.get("nameLua", ""),
                        oper=param_data.get("oper", [])
                    )
                    obj_parameters.append(param)
                    self.parameters.append(param)

                self.parameters_by_obj_id[tech_obj.id] = obj_parameters

            # Загружаем состояния и шаги
            for state_data in data.get("states", []):
                # Создаем состояние
                state = State(
                    id=state_data.get("state_id", ""),
                    name=state_data.get("state_data", {}).get("name", f"state_{state_data.get('state_id', '')}"),
                    operation_id=state_data.get("operation_id", ""),
                    operation_name=state_data.get("operation_name", ""),
                    obj_id=state_data.get("obj_id", ""),
                    obj_name=state_data.get("obj_name", ""),
                    state_data=state_data.get("state_data", {})
                )
                self.states.append(state)

                # Добавляем состояние к соответствующей операции
                if state.operation_id in self.operations_by_id:
                    if state.operation_id not in self.states_by_operation_id:
                        self.states_by_operation_id[state.operation_id] = []
                    self.states_by_operation_id[state.operation_id].append(state)

                # Загружаем шаги для состояния
                state_steps = []
                steps_data = state.state_data.get('steps', {})
                if isinstance(steps_data, dict):
                    for step_id, step_data in steps_data.items():
                        if isinstance(step_data, dict):
                            step = Step(
                                id=f"{state.id}_{step_id}",
                                name=step_data.get("name", f"Шаг {step_id}"),
                                step_number=int(step_id) if str(step_id).isdigit() else 0,
                                state_id=state.id,
                                operation_id=state.operation_id,
                                operation_name=state.operation_name,
                                obj_id=state.obj_id,
                                obj_name=state.obj_name,
                                time_param_n=step_data.get("time_param_n", -1),
                                next_step_n=step_data.get("next_step_n", -1),
                                baseStep=step_data.get("baseStep"),
                                opened_devices=step_data.get("opened_devices", []),
                                closed_devices=step_data.get("closed_devices", []),
                                devices_data=step_data.get("devices_data", []),
                                di_do=step_data.get("DI_DO", []),
                                enable_step_by_signal=step_data.get("enable_step_by_signal"),
                                jump_if=step_data.get("jump_if")
                            )
                            state_steps.append(step)
                            self.steps.append(step)

                            # Добавляем в индекс по state_id
                            if state.id not in self.steps_by_state_id:
                                self.steps_by_state_id[state.id] = []
                            self.steps_by_state_id[state.id].append(step)

                # Сортируем шаги по номеру
                state.steps = sorted(state_steps, key=lambda x: x.step_number)

            print(f"✅ Загружено тех. объектов: {len(self.objects)}")
            print(f"✅ Загружено операций: {len(self.operations)}")
            print(f"✅ Загружено состояний: {len(self.states)}")
            print(f"✅ Загружено шагов: {len(self.steps)}")
            print(f"✅ Загружено параметров: {len(self.parameters)}")

            # Выводим статистику по объектам с операциями
            objects_with_ops = [obj for obj in self.objects if obj.operations]
            print(f"\n📊 Статистика по объектам с операциями:")
            for obj in objects_with_ops:
                print(f"  • {obj.name}: {len(obj.operations)} операций")
                for op in obj.operations[:3]:  # Показываем первые 3 операции
                    states_count = len(self.get_states_for_operation(op.id))
                    steps_count = sum(len(self.get_steps_for_state(s.id)) for s in self.get_states_for_operation(op.id))
                    print(f"    - {op.name}: {states_count} состояний, {steps_count} шагов")

            return True

        except Exception as e:
            print(f"❌ Ошибка загрузки: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _clear(self):
        self.objects.clear()
        self.operations.clear()
        self.states.clear()
        self.steps.clear()
        self.parameters.clear()
        self.objects_by_id.clear()
        self.operations_by_id.clear()
        self.operations_by_obj_id.clear()
        self.states_by_operation_id.clear()
        self.steps_by_state_id.clear()
        self.parameters_by_obj_id.clear()

    def _parse_tech_object(self, data: Dict) -> TechObject:
        return TechObject(
            id=data.get("id", ""),
            n=data.get("n", 0),
            tech_type=data.get("tech_type", 0),
            name=data.get("name", ""),
            name_eplan=data.get("name_eplan", ""),
            name_BC=data.get("name_BC", ""),
            base_tech_object=data.get("base_tech_object", ""),
            attached_objects=data.get("attached_objects"),
            cooper_param_number=data.get("cooper_param_number", -1),
            system_parameters=data.get("system_parameters", {}),
            properties=data.get("properties", {}),
            equipment=data.get("equipment", {})
        )

    def get_object_by_name(self, name: str) -> Optional[TechObject]:
        for obj in self.objects:
            if obj.name == name or obj.name_eplan == name or obj.name_BC == name:
                return obj
        return None

    def get_operations_for_object(self, obj_id: str) -> List[Operation]:
        return self.operations_by_obj_id.get(obj_id, [])

    def get_states_for_operation(self, operation_id: str) -> List[State]:
        return self.states_by_operation_id.get(operation_id, [])

    def get_steps_for_state(self, state_id: str) -> List[Step]:
        return self.steps_by_state_id.get(state_id, [])

    def get_parameters_for_object(self, obj_id: str) -> List[Parameter]:
        return self.parameters_by_obj_id.get(obj_id, [])

    def get_operation_names(self) -> List[str]:
        return sorted([op.name for op in self.operations if op.name])

    def get_operation_by_name(self, name: str) -> Optional[Operation]:
        for op in self.operations:
            if op.name == name:
                return op
        return None

    def get_operation_by_id(self, op_id: str) -> Optional[Operation]:
        return self.operations_by_id.get(op_id)

    def get_object_for_operation(self, operation: Operation) -> Optional[TechObject]:
        return self.objects_by_id.get(operation.obj_id)


# Создаем глобальный экземпляр
objects_data = ObjectsData()