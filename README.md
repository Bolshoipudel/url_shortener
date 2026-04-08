# URL Shortener

Микросервис для сокращения ссылок. Python + FastAPI + PostgreSQL.

## Запуск через Docker Compose

```bash
docker-compose up -d --build
```

FastAPI приложение будет развернуто здесь: `http://localhost:8000`

## API

### Создать короткую ссылку

```bash
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/very/long/path"}'
```

Ответ:
```json
{"short_id": "aBcDeF", "short_url": "http://localhost:8000/aBcDeF"}
```

### Перейти по короткой ссылке

```bash
curl -L http://localhost:8000/aBcDeF
```

### Статистика переходов

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

Тесты используют SQLite и не требуют PostgreSQL
