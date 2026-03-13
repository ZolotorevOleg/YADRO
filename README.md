# currency_service

HTTP-сервис для получения курсов валют через API ЦБ РФ.

## Функциональность

- `GET /info`
- `GET /info/currency?date=YYYY-MM-DD`
- `GET /info/currency?currency=USD`
- `GET /info/currency?date=YYYY-MM-DD&currency=USD`

## Запуск

```bash
pip install -r requirements.txt
python main.py
```
