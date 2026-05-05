from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models import GraphInput, AlgorithmTrace
from app.algorithm import run_tarjan_with_trace

app = FastAPI(title="Tarjan Algorithm Visualizer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене укажите конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Backend is running"}

@app.post("/api/tarjan/run", response_model=AlgorithmTrace)
def run_tarjan(graph: GraphInput):
    """
    Запускает алгоритм Тарьяна на переданном графе.
    Возвращает полный трейс шагов и найденные компоненты.
    """
    try:
        trace, components = run_tarjan_with_trace(graph.nodes, graph.edges)
        return AlgorithmTrace(
            trace=trace,
            components=components,
            total_steps=len(trace)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Algorithm error: {str(e)}")