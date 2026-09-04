# Инструкция по деплою и запуску на сервере (Linux / VPS)

Эта инструкция описывает пошаговый процесс разворачивания бэкенда **"Мой ритм"** на Ubuntu/Debian сервере.

---

## 1. Подготовка сервера и клонирование

Подключитесь к вашему VPS по SSH и выполните команды:

```bash
# Обновление пакетов и установка Python 3.12+ и venv
sudo apt update && sudo apt install -y python3 python3-venv python3-pip git

# Перейдите в папку, где будет жить проект (например, /var/www или ~/apps)
cd /var/www
git clone <URL_ВАШЕГО_РЕПОЗИТОРИЯ> myrhythm-backend
cd myrhythm-backend
```

---

## 2. Настройка виртуального окружения и зависимостей

```bash
# 1. Создаем виртуальное окружение
python3 -m venv .venv

# 2. Активируем его
source .venv/bin/activate

# 3. Обновляем pip и устанавливаем зависимости
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 3. Настройка конфигурации (.env)

Скопируйте пример файла конфигурации и отредактируйте его:

```bash
cp .env.example .env
nano .env
```

Убедитесь, что указаны корректные параметры:
- `JWT_SECRET_KEY` — сгенерируйте случайный стойкий ключ (например: `openssl rand -hex 32`).
- `CORS_ORIGINS` — `*` или конкретный домен вашего фронтенда.
- `ADMIN_EMAIL` и `ADMIN_PASSWORD` — учётные данные главного администратора.

---

## 4. Запуск первичных скриптов (Важно!)

Запускайте скрипты **строго в следующем порядке**:

### Шаг 4.1: Заполнение начальных данных (Стримы / Потоки)
Этот скрипт создаст структуру SQLite базы данных `data/app.db` и заполнит стандартные потоки (Утро, День, Вечер):
```bash
python -m app.seed
```

### Шаг 4.2: Создание учётной записи Администратора
Этот скрипт создаст администратора в БД с данными из `.env` (или запросит их):
```bash
python -m app.create_admin
```

---

## 5. Способы запуска бэкенда

### Вариант А: Быстрый тестовый запуск (в консоли)
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8083
```

---

### Вариант Б: Настройка фонового автозапуска через systemd (РЕКОМЕНДУЕТСЯ)

Чтобы бэкенд автоматически перезапускался при сбоях и при перезагрузке сервера:

1. Создайте файл службы systemd:
```bash
sudo nano /etc/systemd/system/myrhythm.service
```

2. Вставьте следующее содержимое (замените `/var/www/myrhythm-backend` и `user` на ваши реальные пути и пользователя сервера):

```ini
[Unit]
Description=MyRhythm FastAPI Backend Service
After=network.target

[Service]
User=myrhythm
Group=myrhythm
WorkingDirectory=/var/www/myrhythm-backend
ExecStart=/var/www/myrhythm-backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8083 --workers 2 --proxy-headers --forwarded-allow-ips='127.0.0.1'
Restart=always
RestartSec=5
EnvironmentFile=/var/www/myrhythm-backend/.env

[Install]
WantedBy=multi-user.target
```

3. Активируйте и запустите службу:
```bash
sudo systemctl daemon-reload
sudo systemctl enable myrhythm
sudo systemctl start myrhythm

# Проверить статус:
sudo systemctl status myrhythm
```

---

## 6. Настройка Nginx (Reverse Proxy + SSL)

Если вы хотите привязать домен и слушать стандартный HTTPS порт (`443`):

1. Создайте конфигурацию Nginx:
```bash
sudo nano /etc/nginx/sites-available/myrhythm
```

2. Добавьте конфигурацию (обратите внимание на `client_max_body_size` для загрузки видео до 500МБ):

```nginx
server {
    listen 80;
    server_name api.yourdomain.com; # Укажите ваш домен или IP

    # Ограничение размера загружаемых медиафайлов (видео/аудио)
    client_max_body_size 500M;

    location / {
        proxy_pass http://127.0.0.1:8083;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

3. Включите сайт и перезапустите Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/myrhythm /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Полезные команды во время эксплуатации

- **Просмотр логов бэкенда в реальном времени:**
  ```bash
  sudo journalctl -u myrhythm -f
  ```

- **Резервное копирование SQLite БД (без остановки сервера):**
  ```bash
  python -m app.backup
  ```

- **Перезапуск сервера:**
  ```bash
  sudo systemctl restart myrhythm
  ```
