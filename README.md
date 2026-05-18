# Визуализация алгоритма Тарьяна (SCC)

Клиент-серверное приложение для пошаговой визуализации алгоритма Тарьяна поиска сильно связных компонент (Strongly Connected Components) в ориентированном графе.

##  Стек технологий
- **Backend:** Python 3.10+, FastAPI, Pydantic v2, Uvicorn
- **Frontend:** Vanilla JS, Cytoscape.js, HTML5/CSS3
- **Тестирование:** pytest, pytest-cov, httpx
- **Инфраструктура:** CORS, REST API, пошаговый трейс-формат

## Структура проекта
```
tarjan-visualizer/
── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI приложение + эндпоинты
│   │   ├── algorithm.py     # Алгоритм Тарьяна + генератор шагов
│   │   └── models.py        # Pydantic-схемы запросов/ответов
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_algorithm.py # Юнит-тесты алгоритма
│   │   └── test_api.py      # Интеграционные тесты API
│   ├── pytest.ini
│   ├── requirements.txt
│   └── test_manual.py
├── frontend/
│   ├── index.html           # Разметка интерфейса
│   ├── style.css            # Стилизация
│   ├── app.js               # Логика визуализации + API-клиент
│   └── lib/
│       └── cytoscape.min.js # Локальная библиотека графов
└── README.md
```

## Быстрый запуск

### 1. Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
API доступно по: `http://localhost:8000`

### 2. Frontend
```bash
cd frontend
python -m http.server 5500
```
Откройте в браузере: `http://localhost:5500`

### 3. Тесты
```bash
cd backend
pytest -v --cov=app --cov-report=term-missing
```

## API Documentation

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `GET` | `/api/health` | Проверка работоспособности сервера |
| `POST` | `/api/tarjan/run` | Запуск алгоритма. Возвращает полный трейс шагов и найденные SCC |

### Пример запроса `POST /api/tarjan/run`
```json
{
  "nodes": ["1", "2", "3", "4"],
  "edges": [["1", "2"], ["2", "3"], ["3", "1"], ["3", "4"]]
}
```

### Пример ответа
```json
{
  "trace": [ ... ],          
  "components": [["4"], ["1","2","3"]],
  "total_steps": 20
}
```

## 🎮 Управление визуализацией
- **⏮ Назад / Вперёд ⏭** → пошаговое перемещение по трейсу
- **↺ Сброс** → возврат к начальному состоянию
- **Поля ввода** → возможность загрузить произвольный граф (формат: `1,2,3` / `1->2,2->3`)
- **Клавиатура** → `←` `→` навигация, `R` сброс

## Тестовые сценарии
Проект покрывает:
- Пустой граф / 1 вершина / несвязные компоненты
- Циклы, мосты, DAG, полные графы
- Валидацию входных данных (несуществующие вершины, некорректный формат рёбер)
- Структуру трейса и CORS-заголовки

