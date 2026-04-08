# URL Shortener

Микросервис для сокращения ссылок. Python + FastAPI + PostgreSQL.

## Запуск через Docker Compose

```bash
docker-compose up -d --build
```

FastAPI приложение будет развернуто здесь: `http://localhost:8000`

Swagger UI: `http://localhost:8000/docs`

## API

### Создаем короткую ссылку

```bash
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/very/long/path"}'
```

Ответ:
```json
{"short_id": "aBcDeF", "short_url": "http://localhost:8000/aBcDeF"}
```

### Переход по короткой ссылке

```bash
curl http://localhost:8000/aBcDeF
```

Вернёт `307 Temporary Redirect` на оригинальный URL.

### Статистика

```bash
curl http://localhost:8000/stats/aBcDeF
```

Ответ:
```json
{"short_id": "aBcDeF", "original_url": "https://example.com/very/long/path", "clicks": 5}
```

## Тесты

```bash
uv sync
uv run pytest
```

Тесты используют SQLite и не требуют PostgreSQL.
