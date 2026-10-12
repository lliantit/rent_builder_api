# Rent Builder API

Це бекенд для системи оренди будівельних інструментів.

## Налаштування середовища

У проєкті використовуються два середовища: Sandbox (для розробки) та Production (для релізу). Конфігурація відбувається через `.env` файли.

### Запуск у тестовому середовищі (Sandbox)
- Переконайтеся, що файл `.env.sandbox` існує та містить `ENVIRONMENT=sandbox` і `DEBUG=True`.
- Встановіть змінну оточення (Windows PowerShell):
  `$env:ENVIRONMENT="sandbox"`
- Запустіть сервер:
  `uvicorn src.main:app --reload`

### Запуск у робочому середовищі (Production)
- Переконайтеся, що файл `.env.production` існує та містить `ENVIRONMENT=production` і `DEBUG=False`.
- Встановіть змінну оточення:
  `$env:ENVIRONMENT="production"`
- Запустіть сервер:
  `uvicorn src.main:app`