# currency_service

HTTP-сервис для получения курсов валют через API ЦБ РФ.

## Функциональность

- `GET /info`
- `GET /info/currency?date=YYYY-MM-DD`
- `GET /info/currency?currency=USD`
- `GET /info/currency?date=YYYY-MM-DD&currency=USD`

## Переменные окружения

- `VERSION` — версия приложения, по умолчанию `1.0.0`
- `AUTHOR` — автор приложения, по умолчанию `o.zolotorev1`
- `PORT` — порт запуска приложения, по умолчанию `8000`

## Запуск

```
pip install -r requirements.txt
python main.py
```

## Docker Hub

Образ доступен:

`z0leg/currency-service:latest`

## Безопасность
- запуск от non-root пользователя
- read-only файловая система (hardened)
- cap_drop: ALL
- no-new-privileges
- tmpfs для /tmp
- лимиты ресурсов
- healthcheck

## Сканирование
- Trivy → trivy-report.json
- SBOM  → sbom.json