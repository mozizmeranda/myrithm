# Backend веб-сервиса «Мой ритм»

Backend REST API веб-сервиса коротких интервальных тренировок «Мой ритм» на FastAPI, SQLAlchemy 2.x, SQLite (WAL mode) и Redis.

---

## 🚀 Быстрый старт

### 1. Установка зависимости Python 3.12+

Убедитесь, что установлен Python версии 3.12 или выше.

### 2. Создание и активация виртуального окружения

```bash
python -m venv .venv
```

Активация:
* **Windows (PowerShell)**: `.\.venv\Scripts\Activate.ps1`
* **Linux / macOS**: `source .venv/bin/activate`

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения `.env`

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Параметры по умолчанию:
```ini
APP_ENV=development
APP_TIMEZONE=Asia/Tashkent
DATABASE_URL=sqlite:///./data/app.db
REDIS_URL=redis://localhost:6379/0

JWT_SECRET=super-secret-jwt-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30

ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=AdminPassword123!

CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 5. Запуск Redis

Убедитесь, что локально запущен Redis-сервер на `redis://localhost:6379/0`.

### 6. Инициализация базы данных и создание Администратора

Запустите скрипты инициализации:

```bash
# Создаёт таблицы SQLite и базовые потоки тренировок (cardio, back, office, dance, 60plus)
python -m app.seed

# Создаёт единственного администратора системы из параметров .env
python -m app.create_admin
```

### 7. Запуск Backend сервера

```bash
uvicorn app.main:app --reload
```

Приложение будет доступно по адресу: `http://127.0.0.1:8000`

---

## 📖 Документация API (Swagger / ReDoc)

* **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 📹 Локальное хранилище медиафайлов

Медиафайлы (видео упражнений и аудиотреки) добавляются администратором через админ-панель и хранятся локально:

```text
media/
├── videos/
└── audio/
```

FastAPI раздаёт эти файлы по URL-маршрутам вида:
* `/media/videos/<unique_hash>.mp4`
* `/media/audio/<unique_hash>.mp3`

При удалении или замене упражнений/треков unused-файлы автоматически физически удаляются с диска.

---

## 🧪 Запуск тестов (включая race-condition тесты)

Для выполнения unit-тестов, интеграционных тестов и multi-threaded concurrency тестов запустите:

```bash
python -m pytest -v
```

---

## 💾 Безопасный бэкап SQLite

Для создания горячего бэкапа базы данных SQLite с использованием SQLite Online Backup API запустите:

```bash
python -m app.backup
```

Резервная копия сохраняется в директорию `./data/backups/app_backup_YYYYMMDD_HHMMSS.db`.
