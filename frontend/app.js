document.addEventListener("DOMContentLoaded", () => {
  const cy = cytoscape({
    container: document.getElementById("cy-container"),
    elements: [
      { data: { id: "1" } },
      { data: { id: "2" } },
      { data: { id: "3" } },
      { data: { source: "1", target: "2" } },
      { data: { source: "2", target: "3" } },
      { data: { source: "3", target: "1" } }
    ],
    style: [
      { selector: "node", style: { label: "data(id)", width: 40, height: 40, "background-color": "#3b82f6", "text-valign": "center", "text-halign": "center" } },
      { selector: "edge", style: { width: 2, "line-color": "#64748b", "target-arrow-color": "#64748b", "target-arrow-shape": "triangle" } }
    ],
    layout: { name: "grid", padding: 20 }
  });

  console.log("Cytoscape initialized");
});