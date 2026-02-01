# Mirumir

Сервис коллаборативных досок для совместной работы (аналог Miro). Пользователи создают доски, добавляют стикеры, делятся доступом с правами view/edit/owner.

## Стек

- **Backend:** Python 3.13, FastAPI, SQLAlchemy 2 (async + asyncpg), JWT (python-jose), bcrypt, Pydantic
- **Frontend:** Next.js 16, React 19, Tailwind CSS
- **БД:** PostgreSQL 16
- **Оркестрация:** Docker Compose

## Структура репозитория

```
backend/          # API на FastAPI
  api/v1/         # версионированный API, эндпоинты auth, boards, stickers, sharing
  core/            # config, database, security
  models/          # SQLAlchemy-модели (users, boards, accesses, stickers)
  schemas/         # Pydantic-схемы запросов/ответов
  tests/           # pytest, e2e по API

frontend/         # SPA на Next.js (App Router)
  app/             # страницы (auth, boards, board/[id]), компоненты, хуки

docs/             # OpenAPI (auth, boards, stickers, sharing), схема БД (DBML)
docker-compose.yml
```

API описан в `docs/openapi.yaml` и связанных `auth.yaml`, `boards.yaml`, `stickers.yaml`, `sharing.yaml`. Схема БД — в `docs/bd_scheme.dbml`.

## Запуск

### Через Docker Compose

1. В `backend/` создать `.env` из примера:
   ```bash
   cp backend/.env.example backend/.env
   ```
   Заполнить при необходимости (для локальной разработки достаточно значений по умолчанию).

2. Запустить сервисы:
   ```bash
   docker compose up -d
   ```
   - Frontend: http://localhost:3000  
   - Backend: http://localhost:8000  
   - API: http://localhost:8000/api/v1  

### Локально (без Docker)

**Backend**

- Установить [uv](https://docs.astral.sh/uv/#installation), затем в `backend/`: `uv sync`
- PostgreSQL должен быть запущен и доступен по настройкам из `.env` (по умолчанию `POSTGRES_*`).
- Запуск: `uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload`

**Frontend**

- В `frontend/`: `npm install`, при необходимости создать `.env` из `.env.example` (переменная `NEXT_PUBLIC_API_URL` — URL бэкенда).
- Запуск: `npm run dev` (по умолчанию http://localhost:3000)

## Переменные окружения

**Backend** (`backend/.env`): `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` — подключение к PostgreSQL; `SECRET_KEY` — секрет для JWT (в проде обязательно сменить); `ALGORITHM` (по умолчанию HS256), `ACCESS_TOKEN_EXPIRE_MINUTES`, `PROJECT_NAME`.

**Frontend** (`frontend/.env`): `NEXT_PUBLIC_API_URL` — базовый URL бэкенда (например `http://localhost:8000`).

## API (кратко)

- **Auth:** `POST /api/v1/auth/register`, `POST /api/v1/auth/login` — регистрация и вход, в ответе JWT.
- Остальные эндпоинты требуют заголовок `Authorization: Bearer <token>`.
- **Boards:** `GET/POST /api/v1/boards`, `GET/PUT/DELETE /api/v1/boards/{board_id}` — список (фильтр own/shared/all, пагинация, сортировка), создание, просмотр, обновление, удаление.
- **Stickers:** `GET/POST /api/v1/boards/{board_id}/stickers`, `GET/PUT/DELETE .../stickers/{sticker_id}` — CRUD стикеров на доске.
- **Sharing:** `POST/GET/DELETE /api/v1/boards/{board_id}/share` — выдача и отзыв доступа (view/edit).

Права: владелец доски (owner), выданный доступ (view или edit). Подробные контракты — в `docs/*.yaml`.

## Тесты

В каталоге `backend/`: `uv run pytest` (в т.ч. e2e в `tests/e2e/`). Для e2e нужен запущенный бэкенд и БД (например через `docker compose up` только для postgres и backend).
