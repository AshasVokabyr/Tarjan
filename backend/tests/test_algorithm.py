import pytest
from app.algorithm import run_tarjan_with_trace
from app.models import StepState


class TestTarjanAlgorithm:
    """Юнит-тесты алгоритма Тарьяна"""

    @pytest.mark.parametrize("nodes,edges,expected_components", [
        # Пустой граф
        ([], [], []),
        # Одна вершина
        (["A"], [], [["A"]]),
        # Две изолированные вершины
        (["A", "B"], [], [["A"], ["B"]]),
        # Простой цикл (одна компонента)
        (["1", "2", "3"], [["1", "2"], ["2", "3"], ["3", "1"]], [["1", "2", "3"]]),
        # Линейный граф (каждая вершина — отдельная компонента)
        (["1", "2", "3"], [["1", "2"], ["2", "3"]], [["3"], ["2"], ["1"]]),
        # Две компоненты: цикл + изолированная
        (["1", "2", "3", "4"], [["1", "2"], ["2", "3"], ["3", "1"]], [["4"], ["1", "2", "3"]]),
        # Полный граф из 3 вершин (все связаны в обе стороны)
        (["A", "B", "C"], [
            ["A", "B"], ["B", "A"],
            ["B", "C"], ["C", "B"],
            ["A", "C"], ["C", "A"]
        ], [["A", "B", "C"]]),
        # Граф с мостом (две компоненты, соединённые одним ребром)
        (["1", "2", "3", "4"], [["1", "2"], ["2", "1"], ["2", "3"], ["3", "4"], ["4", "3"]], 
         [["1", "2"], ["3", "4"]]),
    ], ids=[
        "empty", "single_node", "two_isolated", "simple_cycle", 
        "linear_dag", "cycle_plus_isolated", "complete_graph", "bridge_graph"
    ])
    def test_scc_correctness(self, nodes, edges, expected_components):
        """Проверяет, что алгоритм находит правильные сильно связные компоненты"""
        trace, components = run_tarjan_with_trace(nodes, edges)
        
        # Сортируем для сравнения (порядок компонент может отличаться)
        components_sorted = [sorted(c) for c in sorted(components)]
        expected_sorted = [sorted(c) for c in sorted(expected_components)]
        
        assert components_sorted == expected_sorted, f"Ожидается {expected_sorted}, получено {components_sorted}"

    def test_trace_structure(self):
        """Проверяет, что трейс имеет правильную структуру шагов"""
        nodes = ["1", "2", "3"]
        edges = [["1", "2"], ["2", "3"], ["3", "1"]]
        
        trace, components = run_tarjan_with_trace(nodes, edges)
        
        assert isinstance(trace, list)
        assert len(trace) > 0
        assert all(isinstance(step, StepState) for step in trace)
        
        # Проверка монотонности шагов
        for i, step in enumerate(trace):
            assert step.step == i
            assert step.action in ["init", "visit", "traverse", "back_edge", "update_low", 
                                  "pop_stack", "component_found", "complete"]
            assert isinstance(step.disc, dict)
            assert isinstance(step.low, dict)
            assert isinstance(step.stack, list)
            assert isinstance(step.on_stack, dict)

    def test_trace_contains_all_phases(self):
        """Проверяет, что трейс содержит ключевые фазы алгоритма"""
        nodes = ["A", "B", "C"]
        edges = [["A", "B"], ["B", "C"], ["C", "A"]]
        
        trace, _ = run_tarjan_with_trace(nodes, edges)
        actions = [step.action for step in trace]
        
        assert "init" in actions
        assert "visit" in actions
        assert "component_found" in actions
        assert "complete" in actions
        assert actions[0] == "init"
        assert actions[-1] == "complete"

    def test_deterministic_output(self):
        """Проверяет детерминизм: одинаковый вход → одинаковый выход"""
        nodes = ["3", "1", "2"]  # Намеренно несортированный порядок
        edges = [["2", "3"], ["1", "2"], ["3", "1"]]
        
        trace1, comp1 = run_tarjan_with_trace(nodes, edges)
        trace2, comp2 = run_tarjan_with_trace(nodes, edges)
        
        # Сравниваем только существенные поля (шаги могут иметь разный ID в metadata)
        assert [(s.action, s.node, tuple(sorted(s.component or []))) for s in trace1] == \
               [(s.action, s.node, tuple(sorted(s.component or []))) for s in trace2]
        assert [sorted(c) for c in sorted(comp1)] == [sorted(c) for c in sorted(comp2)]