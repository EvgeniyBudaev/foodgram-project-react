![yamdb_workflow](https://github.com/EvgeniyBudaev/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat-square&logo=Yandex.Cloud)](https://cloud.yandex.ru/)

# Яндекс.Практикум. Python backend. Diplom

## Содержание
- [Описание_проекта](#Описание_проекта)
- [Технологии](#Технологии)
- [Запуск проекта](#Запуск_проекта)
- [Тесты](#Тесты)
- [Авторы](#Авторы)
- [Список_полезных_команд](#Список_полезных_команд)

### <a name="Описание_проекта">Описание</a>

Foodgram реализован для публикации рецептов. Авторизованные пользователи могут 
подписываться на понравившихся авторов, добавлять рецепты в избранное, 
в покупки, скачать список покупок ингредиентов для добавленных в покупки 
рецептов.

Проект запущен и доступен по [http://62.84.119.85/recipes](http://62.84.119.85/recipes)

### <a name="Технологии">Технологии</a>

В проекте применяется 
- **Django REST Framework**, 
- **Python 3**,
- **PostgreSQL**,
- **Docker**, 
- **Nginx**,
- **Gunicorn**,
- **Git**, 
- Аутентификация реализована с помощью **токена**.

### <a name="Запуск проекта">Запуск проекта</a>

- Установите Docker на ваш сервер:
```python
 sudo apt install docker.io
```

- Установите Docker-compose на сервер:
```python
 sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
 sudo chmod +x /usr/local/bin/docker-compose
```

- Скопируйте на сервер файлы Docker-compose.yml и nginx.conf из папки infra-deploy/. Не забудьте указать свой ip в конфиге.
```python
scp docker-compose.yml admin@62.84.119.85:/home/admin/docker-compose.yml
scp nginx.conf admin@62.84.119.85:/home/admin/nginx.conf
```

- При первом деплоее локально в файле foodgram_workflow.yml в deploy указываем флаг --build:
```python
 sudo docker-compose rm -f backend --build
```

- После успешного деплоя зайдите на боевой сервер и выполните команды (только после первого деплоя):
    Собрать статические файлы в STATIC_ROOT:
```python
  docker-compose exec backend python3 manage.py collectstatic --noinput
```

- После запуска контейнеров выполните команды в терминале:
```python
 docker-compose exec backend python manage.py makemigrations
 docker-compose exec backend python manage.py migrate --noinput
```

- Создаём суперпользователя
```python
 docker-compose exec backend python manage.py createsuperuser
```

- Загружаем ингредиенты в базу данных (необязательно):
```python
 docker-compose exec backend python manage.py loaddata ingredients.json
```

- Запуск контейнеров выполняется командой:
```python
 docker-compose up
```

- Остановка контейнеров выполняется командой:
```python
 docker-compose stop
```

### <a name="Тесты">Тесты</a>
```python
  flake8
```

### <a name="Авторы">Авторы</a>
```
 Евгений Будаев
```

### <a name="Список_полезных_команд">Список полезных команд</a>

- Форматирование кода
- на macOs:
```python
 option + command + L
```
- на windows:
```python
 ctrl + alt + I
```

- Запуск сервера
```python
 python manage.py runserver
```

- Миграции
```python
 python manage.py makemigrations
 python manage.py migrate
```

- Создать супер пользователя
```python
 python manage.py createsuperuser
```

- Создание виртуального окружения
```python
 python -m venv venv
```

- Запуск виртуального окружения проекта
- В Windows:
```python
 .\venv\Scripts\activate
```
- В macOS или Linux:
```python
 source venv/bin/activate
```

- Остановка виртуального окружения
```python
 deactivate
```

- После установки зависимостей выполнить:
```python
 pip freeze > requirements.txt
```
- При клонировании репозитория на другой компьютер или сервер выполните 
-  (предварительно создав и активировав нужное виртуальное окружение):
```python
 pip install -r requirements.txt
```
- Таким образом, разом установятся все необходимые пакеты.

- Установка Django (LTS)
```python
 pip install Django==3.2.9
 python.exe -m pip install --upgrade pip
```

- Создание проекта
```python
 django-admin startproject backend
```

- Создание приложения
```python
 python manage.py startapp users
 python manage.py startapp api
 python manage.py startapp foodgram
```

- Установка PostgreSQL
```python
 pip install psycopg2-binary==2.8.6
```

- Аутентификация по токену. JWT + Djoser.
```python
 pip install djangorestframework
 pip install djoser
```

- CORS
```python
 pip install django-cors-headers
```

- Fixture - выгрузка данных из БД (dump данных)
```python
 python manage.py dumpdata foodgram.Ingredient > ingredients.json
```

- Загрузка данных в БД
```python
 python manage.py loaddata ../data/ingredients.json
```

- Для устранения ошибок I1005,...
```python
 isort .
```

