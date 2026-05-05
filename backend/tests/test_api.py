import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Тесты эндпоинта /api/health"""

    def test_health_check(self):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "Backend is running" in data["message"]


class TestTarjanEndpoint:
    """Тесты эндпоинта /api/tarjan/run"""

    @pytest.mark.parametrize("payload,expected_status,check_components", [
        # Валидные запросы
        ({"nodes": [], "edges": []}, 200, []),
        ({"nodes": ["X"], "edges": []}, 200, [["X"]]),
        ({"nodes": ["1", "2"], "edges": [["1", "2"], ["2", "1"]]}, 200, [["1", "2"]]),
        
        # Невалидные: вершины в рёбрах не существуют
        ({"nodes": ["1"], "edges": [["1", "2"]]}, 422, None),
        ({"nodes": [], "edges": [["1", "2"]]}, 422, None),
        
        # Невалидные: неправильный формат ребра
        ({"nodes": ["1", "2"], "edges": [["1"]]}, 422, None),
        ({"nodes": ["1", "2"], "edges": [["1", "2", "3"]]}, 422, None),
    ], ids=[
        "empty_graph", "single_node", "two_node_cycle",
        "edge_to_missing_node", "edges_without_nodes",
        "edge_single_element", "edge_three_elements"
    ])
    def test_run_tarjan_responses(self, payload, expected_status, check_components):
        """Проверяет статус-коды и базовую структуру ответа"""
        response = client.post("/api/tarjan/run", json=payload)
        assert response.status_code == expected_status
        
        if expected_status == 200 and check_components is not None:
            data = response.json()
            assert "trace" in data
            assert "components" in data
            assert "total_steps" in data
            assert isinstance(data["trace"], list)
            assert isinstance(data["components"], list)
            assert data["total_steps"] == len(data["trace"])
            
            # Проверка компонентов (с сортировкой для надёжности)
            result_comps = [sorted(c) for c in sorted(data["components"])]
            expected_comps = [sorted(c) for c in sorted(check_components)]
            assert result_comps == expected_comps

    def test_response_trace_fields(self):
        """Проверяет, что каждый шаг трейса содержит обязательные поля"""
        payload = {"nodes": ["A", "B"], "edges": [["A", "B"]]}
        response = client.post("/api/tarjan/run", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        required_fields = ["step", "action", "disc", "low", "stack", "on_stack"]
        
        for step in data["trace"]:
            for field in required_fields:
                assert field in step, f"Шаг {step.get('step')} не содержит поле '{field}'"

    def test_cors_headers(self):
        """Проверяет наличие CORS-заголовков"""
        origin = "http://localhost:5500"
        
        response = client.post(
            "/api/tarjan/run", 
            json={"nodes": ["1"], "edges": []},
            headers={"Origin": origin}
        )
        assert response.status_code == 200
        
        # FastAPI отражает конкретный origin, а не "*", если allow_credentials=True
        assert response.headers.get("access-control-allow-origin") == origin
        # Дополнительно можно проверить другие CORS-заголовки:
        assert response.headers.get("vary") == "Origin"  # Указывает, что ответ зависит от Origin