from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Dict, Optional, Any


class GraphInput(BaseModel):
    """Входные данные: ориентированный граф"""
    nodes: List[str] = Field(default_factory=list, description="Список идентификаторов вершин")
    edges: List[List[str]] = Field(default_factory=list, description="Список рёбер [from, to]")

    @model_validator(mode='after')
    def validate_edges_reference_nodes(self):
        """Проверяет, что все вершины в рёбрах существуют в nodes"""
        nodes_set = set(self.nodes)
        for i, edge in enumerate(self.edges):
            if len(edge) != 2:
                raise ValueError(f"Ребро #{i} должно содержать ровно 2 вершины: {edge}")
            src, dst = edge
            if src not in nodes_set:
                raise ValueError(f"Ребро #{i}: вершина '{src}' не найдена в списке nodes")
            if dst not in nodes_set:
                raise ValueError(f"Ребро #{i}: вершина '{dst}' не найдена в списке nodes")
        return self


class StepState(BaseModel):
    """Состояние на одном шаге выполнения алгоритма"""
    step: int = Field(description="Номер шага")
    action: str = Field(description="Тип действия: visit, update_low, push_stack, pop_stack, component_found")
    node: Optional[str] = Field(default=None, description="Текущая вершина")
    edge: Optional[List[str]] = Field(default=None, description="Текущее ребро [from, to]")
    disc: Dict[str, int] = Field(default_factory=dict, description="Время входа (discovery time)")
    low: Dict[str, int] = Field(default_factory=dict, description="Низшее достижимое время (low-link)")
    stack: List[str] = Field(default_factory=list, description="Стек вершин")
    on_stack: Dict[str, bool] = Field(default_factory=dict, description="Флаг: вершина в стеке")
    component: Optional[List[str]] = Field(default=None, description="Найденная компонента")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Доп. информация")


class AlgorithmTrace(BaseModel):
    """Ответ API: полный трейс + результат"""
    trace: List[StepState] = Field(description="Массив шагов алгоритма")
    components: List[List[str]] = Field(description="Список найденных сильно связных компонент")
    total_steps: int = Field(description="Общее количество шагов")