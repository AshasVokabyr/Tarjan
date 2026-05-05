document.addEventListener("DOMContentLoaded", () => {
  const API_URL = "http://localhost:8000/api/tarjan/run";
  const DEFAULT_GRAPH = {
    nodes: ["1", "2", "3", "4"],
    edges: [["1", "2"], ["2", "3"], ["3", "1"], ["3", "4"]]
  };

  let cy = null;
  let trace = [];
  let currentStep = -1; // -1 = начальное состояние

  const $ = id => document.getElementById(id);
  const btnPrev = $("btn-prev");
  const btnNext = $("btn-next");
  const btnReset = $("btn-reset");
  const statusEl = $("status");
  const stackEl = $("stack-display");
  const compEl = $("components-list");
  const logEl = $("log");

  function log(msg) { logEl.textContent = `[${new Date().toLocaleTimeString()}] ${msg}`; }
  function setStatus(text) { statusEl.textContent = text; }
  function updateStack(stack) { stackEl.textContent = `[ ${stack.join(", ")} ]`; }
  
  function updateComponents(comps) {
    if (!comps?.length) { compEl.textContent = "—"; return; }
    compEl.innerHTML = comps.map((c, i) => `<div>SCC #${i + 1}: [${c.join(", ")}]</div>`).join("");
  }

  // Собирает все компоненты, найденные от шага 0 до текущего
  function getFoundComponentsUpToStep(idx) {
    if (idx < 0) return [];
    const comps = [];
    for (let i = 0; i <= idx; i++) {
      if (trace[i].action === "component_found" && trace[i].component) {
        comps.push(trace[i].component);
      }
    }
    return comps;
  }

  function updateButtons() {
    const loaded = trace.length > 0;
    btnPrev.disabled = !loaded || currentStep <= 0;
    btnNext.disabled = !loaded || currentStep >= trace.length - 1;
    btnReset.disabled = !loaded;
  }

  function clearVisuals() {
    if (!cy) return;
    cy.nodes().removeClass("current in-stack in-component visited");
    cy.edges().removeClass("active-edge");
  }

  function applyStep(index) {
    clearVisuals();

    if (index < 0) {
      updateStack([]);
      updateComponents([]); // Сброс списка компонент
      setStatus("Граф загружен. Используйте кнопки навигации.");
      return;
    }

    const step = trace[index];
    const disc = step.disc || {};
    const onStack = step.on_stack || {};

    // 1. Посещённые узлы
    Object.keys(disc).forEach(id => cy.getElementById(id).addClass("visited"));
    // 2. Узлы в стеке
    Object.entries(onStack).forEach(([id, inStack]) => {
      if (inStack) cy.getElementById(id).addClass("in-stack");
    });
    // 3. Текущий узел и ребро
    if (step.node) cy.getElementById(step.node).addClass("current");
    if (step.edge) cy.getElementById(`${step.edge[0]}-${step.edge[1]}`).addClass("active-edge");

    // 4. Обновляем UI
    updateStack(step.stack || []);
    updateComponents(getFoundComponentsUpToStep(index)); // ✅ Динамическое обновление

    const actionNames = {
      "init": "Инициализация",
      "visit": "Посещение узла",
      "traverse": "Переход по ребру",
      "back_edge": "Обратное ребро",
      "update_low": "Обновление low-link",
      "pop_stack": "Извлечение из стека",
      "component_found": "✅ Компонента найдена!",
      "complete": "Алгоритм завершён"
    };
    setStatus(`Шаг ${step.step + 1}/${trace.length}: ${actionNames[step.action] || step.action}`);
  }

  function initCytoscape(graph) {
    const elements = [
      ...graph.nodes.map(id => ({ data: { id, label: id } })),
      ...graph.edges.map(([s, t]) => ({ data: { source: s, target: t, id: `${s}-${t}` } }))
    ];

    cy = cytoscape({
      container: document.getElementById("cy-container"),
      elements,
      style: [
        { selector: "node", style: { label: "data(label)", width: 40, height: 40, "background-color": "#94a3b8", "border-width": 2, "text-valign": "center", "text-halign": "center" } },
        { selector: "edge", style: { width: 2, "line-color": "#94a3b8", "target-arrow-color": "#94a3b8", "target-arrow-shape": "triangle" } },
        { selector: ".current", style: { "background-color": "#ef4444", "border-color": "#b91c1c" } },
        { selector: ".in-stack", style: { "background-color": "#f59e0b", "border-color": "#d97706" } },
        { selector: ".in-component", style: { "background-color": "#10b981", "border-color": "#059669" } },
        { selector: ".visited", style: { "background-color": "#64748b", "border-color": "#475569" } },
        { selector: ".active-edge", style: { "width": 4, "line-color": "#3b82f6", "target-arrow-color": "#3b82f6" } }
      ],
      layout: { name: "circle", padding: 30 }
    });
  }

  async function loadTrace() {
    try {
      setStatus("Загрузка данных...");
      log("Запрос к API...");
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(DEFAULT_GRAPH)
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      
      trace = data.trace;
      currentStep = -1;
      // ❌ Убрали мгновенный вызов updateComponents(data.components)
      log(`✅ Загружено: ${data.total_steps} шагов, ${data.components.length} SCC`);
      updateButtons();
      setStatus("Граф загружен. Используйте ⏮ Вперёд ⏭ ↺");
    } catch (err) {
      log(`❌ Ошибка: ${err.message}`);
      setStatus("Ошибка загрузки данных");
    }
  }

  btnPrev.addEventListener("click", () => {
    if (currentStep > 0) {
      currentStep--;
      applyStep(currentStep);
      updateButtons();
    }
  });

  btnNext.addEventListener("click", () => {
    if (currentStep < trace.length - 1) {
      currentStep++;
      applyStep(currentStep);
      updateButtons();
    }
  });

  btnReset.addEventListener("click", () => {
    currentStep = -1;
    applyStep(currentStep);
    updateButtons();
    log("↺ Визуализация сброшена");
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "ArrowLeft" && !btnPrev.disabled) btnPrev.click();
    if (e.key === "ArrowRight" && !btnNext.disabled) btnNext.click();
    if (e.key.toLowerCase() === "r" && !btnReset.disabled) btnReset.click();
  });

  initCytoscape(DEFAULT_GRAPH);
  loadTrace();
});