# objects_loader.py
import json

import config
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
        # Сигналы проекта (DI_DO и прочие): секция в выгрузке была всегда,
        # а разбор её пропускал — до потребителя они не доезжали никак
        self.signals: List[Dict[str, Any]] = []

        # Словари для быстрого доступа
        self.objects_by_id: Dict[str, TechObject] = {}
        self.operations_by_id: Dict[str, Operation] = {}
        self.operations_by_obj_id: Dict[str, List[Operation]] = {}
        self.states_by_operation_id: Dict[str, List[State]] = {}
        self.steps_by_state_id: Dict[str, List[Step]] = {}
        self.parameters_by_obj_id: Dict[str, List[Parameter]] = {}

        # Индекс «устройство → где оно открывается и закрывается».
        # Считается лениво и один раз: выгрузке нужны состояния всех
        # устройств листа, а перебирать ради каждого все состояния и шаги
        # означало бы 233 x 247 проходов на контрольном листе
        self._device_states: Optional[Dict[str, List[Dict[str, Any]]]] = None

    def load(self, file_path: str | None = None) -> bool:
        # Читает JSON и раскладывает данные по объектной модели.
        # Раньше здесь была вторая копия разбора, дублировавшая load_from_json;
        # реализация оставлена одна.
        file_path = file_path or str(config.PARSED_LUA_OBJECTS_JSON)
        try:
            if not Path(file_path).exists():
                print(f"❌ Файл не найден: {file_path}")
                return False

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.load_from_json(data)
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
        self.signals.clear()
        self.objects_by_id.clear()
        self.operations_by_id.clear()
        self.operations_by_obj_id.clear()
        self.states_by_operation_id.clear()
        self.steps_by_state_id.clear()
        self.parameters_by_obj_id.clear()
        self._device_states = None

    @staticmethod
    def _parse_tech_object(data: Dict) -> TechObject:
        # Разбор техобъекта был написан дважды: здесь и повторно внутри
        # load_from_json, слово в слово. Этот метод при этом никто не звал,
        # то есть расходиться копии начали бы незаметно
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

    def load_from_json(self, data: dict):
        # Загружает данные из JSON словаря
        self._clear()

        # Временные словари для индексов
        _operations_by_id = {}
        _states_by_operation = {}
        _steps_by_state = {}
        _parameters_by_object = {}

        # Загружаем технологические объекты
        for obj_data in data.get("tech_objects", []):
            tech_obj = self._parse_tech_object(obj_data)

            # Загружаем операции
            obj_operations = []
            for op_data in obj_data.get("operations", []):
                operation = Operation(
                    id=op_data.get("id", ""),
                    name=op_data.get("name", ""),
                    base_operation=op_data.get("base_operation", ""),
                    obj_id=tech_obj.id,
                    obj_name=tech_obj.name,
                    props=op_data.get("props", {})
                )
                obj_operations.append(operation)
                self.operations.append(operation)
                _operations_by_id[operation.id] = operation

            tech_obj.operations = obj_operations
            self.objects.append(tech_obj)
            self.objects_by_id[tech_obj.id] = tech_obj
            self.operations_by_obj_id[tech_obj.id] = obj_operations

        # Загружаем параметры
        for param_data in data.get("parameters", []):
            param = Parameter(
                id=param_data.get("id", ""),
                name=param_data.get("name", ""),
                value=param_data.get("value", 0),
                meter=param_data.get("meter", ""),
                nameLua=param_data.get("nameLua", ""),
                oper=param_data.get("oper", [])
            )
            self.parameters.append(param)
            obj_id = param_data.get("obj_id", "")
            if obj_id not in _parameters_by_object:
                _parameters_by_object[obj_id] = []
            _parameters_by_object[obj_id].append(param)

        self.parameters_by_obj_id = _parameters_by_object

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
            if state.operation_id not in _states_by_operation:
                _states_by_operation[state.operation_id] = []
            _states_by_operation[state.operation_id].append(state)

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
                        if state.id not in _steps_by_state:
                            _steps_by_state[state.id] = []
                        _steps_by_state[state.id].append(step)

            # Сортируем шаги по номеру
            state.steps = sorted(state_steps, key=lambda x: x.step_number)

        self.signals = list(data.get("signals", []))
        self.states_by_operation_id = _states_by_operation
        self.steps_by_state_id = _steps_by_state
        self.operations_by_id = _operations_by_id

        print(f"✅ Загружено тех. объектов: {len(self.objects)}")
        print(f"✅ Загружено операций: {len(self.operations)}")
        print(f"✅ Загружено состояний: {len(self.states)}")
        print(f"✅ Загружено шагов: {len(self.steps)}")
        print(f"✅ Загружено параметров: {len(self.parameters)}")
        print(f"✅ Загружено сигналов: {len(self.signals)}")


    def get_devices_for_operation(self, operation_id: str) -> Dict[str, str]:
        # Возвращает словарь {имя_устройства: статус} для операции
        devices_status = {}

        # Получаем все состояния операции
        states = self.get_states_for_operation(operation_id)

        for state in states:
            # Проверяем устройства в состоянии
            opened = state.state_data.get("opened_devices", [])
            if isinstance(opened, list):
                for dev in opened:
                    dev_name = self._extract_device_name(dev)
                    if dev_name:
                        devices_status[dev_name] = "opened"

            closed = state.state_data.get("closed_devices", [])
            if isinstance(closed, list):
                for dev in closed:
                    dev_name = self._extract_device_name(dev)
                    if dev_name:
                        devices_status[dev_name] = "closed"

            # Проверяем devices_data
            devices_data = state.state_data.get("devices_data", [])
            if isinstance(devices_data, list):
                for group in devices_data:
                    if isinstance(group, dict):
                        group_devices = group.get("devices", [])
                        if isinstance(group_devices, list):
                            for dev in group_devices:
                                dev_name = self._extract_device_name(dev)
                                if dev_name:
                                    devices_status[dev_name] = "opened"

            # Проверяем шаги состояния
            steps = self.get_steps_for_state(state.id)
            for step in steps:
                for dev in step.opened_devices:
                    dev_name = self._extract_device_name(dev)
                    if dev_name:
                        devices_status[dev_name] = "opened"

                for dev in step.closed_devices:
                    dev_name = self._extract_device_name(dev)
                    if dev_name:
                        devices_status[dev_name] = "closed"

        return devices_status

    def get_device_details_in_operation(self, operation_id: str, device_name: str) -> Optional[Dict]:
        # Возвращает детальную информацию об устройстве в операции
        states = self.get_states_for_operation(operation_id)

        for state in states:
            # Проверяем состояние
            opened = state.state_data.get("opened_devices", [])
            if isinstance(opened, list):
                for dev in opened:
                    if self._extract_device_name(dev) == device_name:
                        return {
                            "status": "opened",
                            "state_name": state.name,
                            "step_name": None,
                            "step_number": -1
                        }

            closed = state.state_data.get("closed_devices", [])
            if isinstance(closed, list):
                for dev in closed:
                    if self._extract_device_name(dev) == device_name:
                        return {
                            "status": "closed",
                            "state_name": state.name,
                            "step_name": None,
                            "step_number": -1
                        }

            # Проверяем шаги
            steps = self.get_steps_for_state(state.id)
            for step in steps:
                for dev in step.opened_devices:
                    if self._extract_device_name(dev) == device_name:
                        return {
                            "status": "opened",
                            "state_name": state.name,
                            "step_name": step.name,
                            "step_number": step.step_number
                        }

                for dev in step.closed_devices:
                    if self._extract_device_name(dev) == device_name:
                        return {
                            "status": "closed",
                            "state_name": state.name,
                            "step_name": step.name,
                            "step_number": step.step_number
                        }

        return None

    # ------------------------------------------------ состояния всех устройств

    def get_device_states(self, device_name: str) -> List[Dict[str, Any]]:
        """Все места, где устройство открывается или закрывается.

        В отличие от get_device_details_in_operation, который отвечает про
        одну выбранную операцию и возвращает первое совпадение, здесь — весь
        список: операция, состояние, шаг и что с устройством происходит.
        Именно это уходит в выгрузку, чтобы редактор мог
        показать положение клапана на каждом шаге мойки, а не только
        в текущей операции.
        """
        if not device_name:
            return []
        if self._device_states is None:
            self._device_states = self._build_device_states()
        return self._device_states.get(device_name, [])

    def get_operation_device_states(self, operation_id: str) -> List[Dict[str, Any]]:
        """То же самое, но со стороны операции: что она делает с устройствами.

        `get_device_states` отвечает «где участвует вот это устройство»,
        здесь — «какие устройства участвуют вот в этой операции». Индекс
        один и тот же, поэтому окно, показывая операцию и устройство,
        не может рассказать про них разное.

        Имя устройства приходит полем `device`, остальное — как в индексе.
        """
        if not operation_id:
            return []
        if self._device_states is None:
            self._device_states = self._build_device_states()

        places = [dict(entry, device=device)
                  for device, entries in self._device_states.items()
                  for entry in entries
                  if entry["operation_id"] == operation_id]
        # Порядок задаётся содержимым, а не порядком обхода словаря
        places.sort(key=lambda e: (e["state"], e["state_id"], e["step_number"],
                                   e["step"], e["device"], e["status"]))
        return places

    def _build_device_states(self) -> Dict[str, List[Dict[str, Any]]]:
        # Один проход по всем состояниям и шагам вместо прохода на устройство
        index: Dict[str, List[Dict[str, Any]]] = {}
        seen: Dict[str, set] = {}

        def add(device: Any, entry: Dict[str, Any]):
            name = self._extract_device_name(device)
            if not name:
                return
            # Устройство попадает в список и состоянием, и его шагом —
            # один и тот же факт не должен уехать дважды
            mark = (entry["operation_id"], entry["state_id"],
                    entry["step_id"], entry["status"])
            if mark in seen.setdefault(name, set()):
                return
            seen[name].add(mark)
            index.setdefault(name, []).append(entry)

        def entry(state: State, step: Optional[Step], status: str) -> Dict[str, Any]:
            return {
                "operation_id": state.operation_id,
                "operation": state.operation_name,
                # Имя техобъекта в описании операций не уникально («Танк»
                # носят все восемь), поэтому рядом идёт и его идентификатор
                "tech_object": state.obj_name,
                "tech_object_id": state.obj_id,
                "state_id": state.id,
                "state": state.name,
                "step_id": step.id if step else "",
                "step": step.name if step else "",
                "step_number": step.step_number if step else -1,
                "status": status,
            }

        for state in self.states:
            for key, status in (("opened_devices", "opened"),
                                ("closed_devices", "closed")):
                for device in state.state_data.get(key, []) or []:
                    add(device, entry(state, None, status))

            # devices_data — устройства, которыми управляет сигнал: их
            # положение задано группой, а не списком открытых
            for group in state.state_data.get("devices_data", []) or []:
                if isinstance(group, dict):
                    for device in group.get("devices", []) or []:
                        add(device, entry(state, None, "opened"))

            for step in self.get_steps_for_state(state.id):
                for device in step.opened_devices:
                    add(device, entry(state, step, "opened"))
                for device in step.closed_devices:
                    add(device, entry(state, step, "closed"))
                for group in step.devices_data or []:
                    if isinstance(group, dict):
                        for device in group.get("devices", []) or []:
                            add(device, entry(state, step, "opened"))

        # Порядок задаётся содержимым, а не порядком обхода: одинаковый
        # проект должен давать одинаковый файл
        for entries in index.values():
            entries.sort(key=lambda e: (e["operation"], e["operation_id"],
                                        e["state"], e["step_number"],
                                        e["step"], e["status"]))

        return index

    def get_object_details(self, obj_id: str) -> Optional[Dict[str, Any]]:
        """Всё, что описание знает о техобъекте, кроме операций.

        Уставки, свойства, состав оборудования и системные параметры —
        то, что относится к объекту, а не к отдельному устройству. В выгрузку
        не попадало ничего из этого: файл нёс операции и шаги, но не то,
        чем объект настроен.
        """
        tech_object = self.objects_by_id.get(obj_id)
        if not tech_object:
            return None

        details: Dict[str, Any] = {
            "id": tech_object.id,
            "n": tech_object.n,
            "name": tech_object.name,
            "name_eplan": tech_object.name_eplan,
            "name_BC": tech_object.name_BC,
            "base_tech_object": tech_object.base_tech_object,
            "tech_type": tech_object.tech_type,
        }
        if tech_object.properties:
            details["properties"] = tech_object.properties
        if tech_object.equipment:
            details["equipment"] = tech_object.equipment
        if tech_object.system_parameters:
            details["system_parameters"] = tech_object.system_parameters

        parameters = self.get_parameters_for_object(obj_id)
        if parameters:
            details["parameters"] = [
                {"id": p.id, "name": p.name, "value": p.value,
                 "meter": p.meter, "nameLua": p.nameLua, "oper": p.oper}
                for p in parameters]

        return details

    def get_operation_program(self, operation_id: str) -> Optional[Dict[str, Any]]:
        """Программа операции: её состояния, шаги и что каждый шаг делает.

        Нужна выгрузке, чтобы вместе со схемой уезжало и то, что на ней
        происходит: не только «клапан открыт», но и в каком шаге какой
        операции. Ищется по идентификатору, а не по имени техобъекта:
        имя объекта на чертеже (`+BRINE_TANK1`) и его имя в описании
        операций («Танк рассола») — разные вещи, а идентификатор операции
        приходит вместе с состоянием устройства.
        """
        operation = self.get_operation_by_id(operation_id)
        if not operation:
            return None

        states = []
        for state in self.get_states_for_operation(operation.id):
            steps = []
            # Шаги в индексе лежат в порядке разбора, а в выгрузку должны
            # уехать по номеру: редактор читает их подряд
            for step in sorted(self.get_steps_for_state(state.id),
                               key=lambda s: s.step_number):
                steps.append({
                    "number": step.step_number,
                    "name": step.name,
                    "opened_devices": [self._extract_device_name(d)
                                       for d in step.opened_devices],
                    "closed_devices": [self._extract_device_name(d)
                                       for d in step.closed_devices],
                })
            states.append({"id": state.id, "name": state.name, "steps": steps})

        return {"id": operation.id, "name": operation.name,
                "tech_object": operation.obj_name,
                "base_operation": operation.base_operation,
                "states": states}

    def _extract_device_name(self, device: Any) -> str:
        if isinstance(device, str):
            # Убираем возможные префиксы и суффиксы
            device = device.strip()
            # Если есть пробелы, берем первое слово
            if ' ' in device:
                device = device.split()[0]
            # Убираем кавычки если есть
            device = device.strip('"\'')
            return device
        elif isinstance(device, dict):
            # Если это словарь, ищем имя
            for key in ['name', 'device', 'id', 'dev']:
                if key in device:
                    return str(device[key])
        elif isinstance(device, (int, float)):
            return str(device)
        return None


# Создаем глобальный экземпляр
objects_data = ObjectsData()
