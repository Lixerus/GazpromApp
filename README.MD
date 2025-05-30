# Device Monitoring API

REST API для сбора и анализа данных с устройств с использованием FastAPI и Celery.

## 📋 Описание

Сервис предоставляет:
- Запись показаний устройств (`x`, `y`, `z` координаты)
- Асинхронный расчет статистики (min/max/median/sum/count)
- Нагрузочное тестирование

## 🛠 Технологии

- Python 3.12
- FastAPI
- Celery + Redis
- PostgreSQL
- SQLAlchemy 2.0
- Locust (тестирование)

## 🚀 Запуск

### 1. Клонирование репозитория
```bash
git clone https://github.com/Lixerus/GazpromApp.git
cd GazpromApp
docker-compose up --build
```

 Для завершения работы выполните

```bash
docker-compose down
```
Для удаления всех docker ресурсов проекта выполните
```bash
docker-compose down --rmi all -v 
``` 

## 4. Документация :

## 📊 API Endpoints

### Без аутентификации

| Метод | Путь                     | Описание                     |
|-------|--------------------------|------------------------------|
| POST  | `/devices/upload`        | Запись новых измерений       |
| GET   | `/devices/stats/all`     | Статистика по всем данным    |
| GET   | `/devices/stats/grouped` | Статистика с группировкой    |
|GET    |`/devices/tasks/{task_id}`| Проверки статуса асинхронных задач|

API: *http://localhost:8000/docs*


## 📈5 Нагрузочное тестирование
Запуск Locust локально из корневой папки(при наличии зависисмостей):

``` bash
locust -f locustfile.py
``` 
Интерфейс Locust: http://localhost:8089
Параметры тестирования: Максимум пользователей: 300, прирост : 5 пользователей.

Результаты:
Можно посмотреть на картинках в репозитории.

![статистика по запросам](total_requests_per_second_1745158716.png)
![пропорциональность запров](2locratio.PNG)