# URL Shortener API 🔗

Сервис сокращения ссылок с аналитикой, аутентификацией и кэшированием.

## 🚀 Функционал

### Обязательные функции:
- ✅ Создание коротких ссылок (POST /api/links/shorten)
- ✅ Редирект с короткой ссылки на оригинал (GET /{short_code})
- ✅ Удаление ссылок (DELETE /api/links/{short_code})
- ✅ Обновление ссылок (PUT /api/links/{short_code})
- ✅ Статистика по ссылкам (клики, дата создания, последнее использование)
- ✅ Кастомные алиасы (уникальный short_code)
- ✅ Поиск ссылок по оригинальному URL
- ✅ Время жизни ссылок (автоматическое удаление после expires_at)

### Дополнительные функции:
- 🔐 JWT аутентификация (регистрация/вход)
- 👤 Управление только своими ссылками
- 📊 История всех ссылок пользователя
- ⚡ Redis кэширование популярных ссылок
- 🗑️ Очистка кэша при обновлении/удалении
- 🎨 Красивый frontend интерфейс

## 🛠 Технологии

- **Backend**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Auth**: JWT (python-jose)
- **Password Hashing**: Argon2 (passlib)
- **Frontend**: HTML5 + CSS3 + Vanilla JavaScript

## 📦 Установка и запуск

### 1. Клонирование репозитория

```bash
git clone https://github.com/RussiaMafia/url-shortener.git
cd url-shortener
```
### 2. Создание виртуального окружения

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```
### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```
### 4. Настройка переменных окружения

Создайте файл .env в корне проекта:
```.env
# Database
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/url_shortener

# Redis
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App settings
BASE_URL=http://localhost:8000
DEFAULT_LINK_EXPIRATION_DAYS=30
SHORT_CODE_LENGTH=6
CACHE_TTL=3600
```
### 5. Запуск базы данных и Redis
```bash
# Используя Docker
docker-compose up postgres redis -d
```
# Или установите PostgreSQL и Redis локально

### 6. Применение миграций
```bash
alembic upgrade head
```
### 7. Запуск приложения
```bash
# Backend API
uvicorn app.main:app --reload

# Frontend (отдельно)
cd frontend
python -m http.server 3000
# или используйте Live Server в VS Code
```
## Приложение доступно:
API: http://localhost:8000
Swagger документация: http://localhost:8000/docs
Frontend: http://localhost:3000/frontend/index.html

## 🐳 Docker Compose
Для запуска всего стека одной командой:
```bash
docker-compose up --build
```
## 📚 API Endpoints
### Authentication
Метод       Endpoint        Описание
POST        /api/auth/register      Регистрация нового пользователя
POST        /api/auth/login     Вход и получение JWT токена
GET     /api/auth/me        Информация о текущем пользователе

### Links
Метод       Endpoint        Описание        Auth
POST        /api/links/shorten      Создать короткую ссылку     Опционально
GET     /{short_code}       🔗 Редирект на оригинал     Нет
GET     /api/links/{code}/stats     Статистика по ссылке        Опционально
PUT     /api/links/{code}       Обновить ссылку     Да (владелец)
DELETE      /api/links/{code}       Удалить ссылку      Да (владелец)
GET     /api/links/my       Мои ссылки      Да
GET     /api/links/search       Поиск по URL        Опционально

## 🗄️ База данных
### Таблица users
* id — Primary Key
* email — уникальный email
* hashed_password — хэш пароля (Argon2)
* is_active — статус аккаунта
* created_at, updated_at — временные метки
### Таблица short_links
* id — Primary Key
* short_code — уникальный код (6 символов)
* original_url — исходная ссылка
* custom_alias — пользовательский алиас
* expires_at — дата истечения
* click_count — счётчик переходов
* last_accessed_at — последний переход
* owner_id — Foreign Key на users
## ⚡ Кэширование
Используется Redis для кэширования:
* Популярных ссылок (TTL: 1 час)
* Автоматическая очистка при обновлении/удалении
* Ускорение редиректов
## 🔐 Безопасность
* Пароли хэшируются алгоритмом Argon2
* JWT токены с истекающим сроком
* CORS настроен для безопасности
* Валидация данных через Pydantic
* Защита от SQL-инъекций (SQLAlchemy ORM)

## Структура проекта

FastAPI/
├── app/
│   ├── api/              # API endpoints
│   │   ├── __init__.py
│   │   ├── auth.py       # Аутентификация
│   │   ├── links.py      # CRUD ссылок
│   │   └── redirect.py   # Публичный редирект
│   ├── core/             # Конфигурация
│   │   ├── config.py     # Настройки
│   │   ├── database.py   # PostgreSQL
│   │   └── redis_client.py # Redis
│   ├── models/           # SQLAlchemy модели
│   │   ├── base.py
│   │   ├── user.py
│   │   └── link.py
│   ├── schemas/          # Pydantic схемы
│   │   ├── user.py
│   │   └── link.py
│   ├── services/         # Бизнес-логика
│   │   ├── auth.py
│   │   └── link_service.py
│   └── main.py           # Точка входа
├── alembic/              # Миграции БД
├── frontend/             # HTML/CSS/JS интерфейс
│   ├── index.html
│   ├── css/style.css
│   └── js/app.js
├── tests/                # Тесты
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
