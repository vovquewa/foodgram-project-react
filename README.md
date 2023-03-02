# Foodgram
Социальная сеть фудблоггеров. Есть возможность создавать рецепты, добавлять в избранное, формировать список покупок.


## Статус workflow
![Workflow status](https://github.com/vovquewa/foodgram-project-react/actions/workflows/main.yml/badge.svg)


## Стек технологий
[![My Tech Stack](https://github-readme-tech-stack.vercel.app/api/cards?title=&lineCount=2&line1=react,react,5f34a6;django,django,34d582;django,drf,01ac74;postgresql,postgresql,3e8d8a;&line2=python,python%203.10,505f68;nginx,nginx,924fc9;docker,docker,b0e078;)](https://github-readme-tech-stack.vercel.app/api/cards?title=&lineCount=2&line1=react,react,5f34a6;django,django,34d582;django,drf,01ac74;postgresql,postgresql,3e8d8a;&line2=python,python%203.10,505f68;nginx,nginx,924fc9;docker,docker,b0e078;)

## Реквизиты проекта

Foodgram **http://ivovq.ru**.

API **http://ivovq.ru/api/**.

API doc: **http://ivovq.ru/api/redoc/**.


## .env

**Замечание**
Для docker-compose файла версии 3.5 файл .env не должен содержать комментариев

```.env
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=password # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
DJANGO_SECRET_KEY=django-insecure-asmd,pasmfoep # секретный ключ джанги
```

### Автор проекта
[vovquewa](https://github.com/vovquewa)
