from typing import List, Dict, Set, Optional, Any
from collections import defaultdict
from app.models import StepState


class TarjanVisualizer:
    """
    Алгоритм Тарьяна для поиска сильно связных компонент (SCC)
    с генерацией шагов для пошаговой визуализации.
    """

    def __init__(self, nodes: List[str], edges: List[List[str]]):
        self.nodes = set(nodes)
        self.adj: Dict[str, List[str]] = defaultdict(list)
        for src, dst in edges:
            self.adj[src].append(dst)
        
        # Состояние алгоритма
        self.index_counter = 0
        self.stack: List[str] = []
        self.lowlink: Dict[str, int] = {}
        self.index: Dict[str, int] = {}
        self.on_stack: Dict[str, bool] = {}
        self.components: List[List[str]] = []
        
        # Трейс для визуализации
        self.trace: List[StepState] = []

    def _add_step(self, action: str, node: Optional[str] = None, 
                  edge: Optional[List[str]] = None, component: Optional[List[str]] = None,
                  metadata: Optional[Dict[str, Any]] = None):
        """Добавляет шаг в трейс с текущим состоянием"""
        self.trace.append(StepState(
            step=len(self.trace),
            action=action,
            node=node,
            edge=edge,
            disc=dict(self.index),
            low=dict(self.lowlink),
            stack=list(self.stack),
            on_stack=dict(self.on_stack),
            component=component,
            metadata=metadata
        ))

    def _strongconnect(self, v: str):
        """Рекурсивная функция strongconnect с логированием шагов"""
        # Устанавливаем индекс вершины
        self.index[v] = self.index_counter
        self.lowlink[v] = self.index_counter
        self.index_counter += 1
        self.stack.append(v)
        self.on_stack[v] = True
        
        self._add_step("visit", node=v, metadata={"index": self.index[v], "lowlink": self.lowlink[v]})

        # Перебираем соседей
        for w in self.adj[v]:
            edge = [v, w]
            
            if w not in self.index:
                # Вершина ещё не посещена — рекурсивный вызов
                self._add_step("traverse", node=v, edge=edge, metadata={"direction": "forward"})
                self._strongconnect(w)
                self.lowlink[v] = min(self.lowlink[v], self.lowlink[w])
                self._add_step("update_low", node=v, edge=edge, 
                              metadata={"new_low": self.lowlink[v], "from": self.lowlink[w]})
            elif self.on_stack.get(w, False):
                # Обратное ребро к вершине в стеке
                self._add_step("back_edge", node=v, edge=edge, metadata={"target_low": self.lowlink[w]})
                self.lowlink[v] = min(self.lowlink[v], self.index[w])
                self._add_step("update_low", node=v, edge=edge,
                              metadata={"new_low": self.lowlink[v], "from": self.index[w]})

        # Если вершина — корень компоненты
        if self.lowlink[v] == self.index[v]:
            component = []
            while True:
                w = self.stack.pop()
                self.on_stack[w] = False
                component.append(w)
                self._add_step("pop_stack", node=w, metadata={"component_building": True})
                
                if w == v:
                    break
            
            component.sort()  # Для детерминированного вывода
            self.components.append(component)
            self._add_step("component_found", node=v, component=component,
                          metadata={"component_id": len(self.components)})

    def run(self) -> tuple[List[StepState], List[List[str]]]:
        """Запускает алгоритм и возвращает (трейс, компоненты)"""
        # Инициализация
        self.index_counter = 0
        self.stack = []
        self.lowlink = {}
        self.index = {}
        self.on_stack = {}
        self.components = []
        self.trace = []
        
        self._add_step("init", metadata={"nodes": sorted(self.nodes), "edges_count": len(self.adj)})
        
        # Запускаем DFS для всех непосещённых вершин (для несвязных графов)
        for node in sorted(self.nodes):  # sorted для детерминизма
            if node not in self.index:
                self._strongconnect(node)
        
        self._add_step("complete", metadata={"components_count": len(self.components)})
        
        return self.trace, self.components


def run_tarjan_with_trace(nodes: List[str], edges: List[List[str]]) -> tuple[List[StepState], List[List[str]]]:
    """Удобная функция-обёртка для запуска алгоритма"""
    visualizer = TarjanVisualizer(nodes, edges)
    return visualizer.run()