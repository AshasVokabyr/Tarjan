# backend/test_manual.py
from app.algorithm import run_tarjan_with_trace

# Простой тест: цикл 1→2→3→1 (одна SCC) + изолированная вершина 4
nodes = ["1", "2", "3", "4"]
edges = [["1", "2"], ["2", "3"], ["3", "1"], ["3", "4"]]

trace, components = run_tarjan_with_trace(nodes, edges)

print(f"✅ Найдено компонент: {len(components)}")
print(f"📦 Компоненты: {components}")
print(f"📊 Всего шагов: {len(trace)}")
print(f"\n🔍 Первые 5 шагов:")
for i, step in enumerate(trace[:5]):
    print(f"  {i}. {step.action} | node={step.node} | stack={step.stack}")