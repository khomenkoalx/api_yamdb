# Проект YaMDb
Проект YaMDb собирает отзывы пользователей на произведения. Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку, зато можно подобрать себе что-нибудь интересное на вечер, оставить отзыв (рецензию), и даже обсудить рецензию в комментариях.

## Авторы
Герман Ермилов - @germanermiloff  
Даниил Горнин - @dgornin  
Александр Хоменко - @khomenkoalx

## Использованные технологии
Python 3.9.13
Django 3.2
djangorestframework 3.12.4
pandas 2.2.3

## Развертывание проекта
Клонируйте репозиторий и перейдите в директорию api_yamdb
```bash
git clone https://github.com/khomenkoalx/api_yamdb
cd api_yamdb
```

Создайте и активируйте виртуальное окружение
```bash
python -m venv venv
source venv/Scripts/activate
```

Установите необходимые зависимости
```bash
pip install -r requirements.txt
```

Перейдите в корневую директорию проекта и выполните миграции
```bash
cd api_yamdb
python manage.py migrate
```

## Импорт данных
Для демонстрации работы приложения заготовлены данные в формате **.csv**. Для их импорта в базу данных проекта используйте консольную команду `csv_parser`.
```bash
python manage.py csv_parser --path static/data/category.csv --model Category
python manage.py csv_parser --path static/data/genre.csv --model Genre
python manage.py csv_parser --path static/data/users.csv --model Users
python manage.py csv_parser --path static/data/titles.csv --model Title
python manage.py csv_parser --path static/data/genre_title.csv --model GenreTitle
python manage.py csv_parser --path static/data/review.csv --model Review
python manage.py csv_parser --path static/data/comments.csv --model Comment
```

## Запуск приложения
Для запуска приложения используйте сервер разработки
```bash
python manage.py runserver
```
Рабочее приложение будет доступно по адресу `http://127.0.0.1:8000/`.
Посмотреть доступные эндпоинты можно по адресу `http://127.0.0.1:8000/api/v1/`

## Справка о приложении
Документация API приложения доступна по адресу `http://127.0.0.1:8000/api/v1/redoc/`
