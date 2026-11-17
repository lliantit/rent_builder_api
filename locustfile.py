import requests
from locust import HttpUser, between, events, task

# Глобальний токен, щоб 50 юзерів не клали базу одночасним хешуванням bcrypt при старті
SHARED_HEADERS = {}


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Виконується ОДИН раз перед запуском усіх користувачів"""
    global SHARED_HEADERS
    host = environment.host or "http://localhost"
    email = "admin@mail.com"
    password = "admin"

    # 1. Реєструємо користувача один раз (ігноруємо, якщо вже існує)
    try:
        requests.post(
            f"{host}/register",
            json={"email": email, "password": password, "role": "admin"},
            timeout=5,
        )
    except Exception:
        pass

    # 2. Отримуємо токен один раз для пулу тестування
    resp = requests.post(
        f"{host}/login",
        data={"username": email, "password": password},
        timeout=5,
    )
    if resp.status_code != 200:
        resp = requests.post(
            f"{host}/login",
            json={"email": email, "password": password},
            timeout=5,
        )

    if resp.status_code == 200:
        token = resp.json().get("access_token")
        SHARED_HEADERS = {"Authorization": f"Bearer {token}"}
        print("✅ Успішно отримано токен для навантажувального тестування!")
    else:
        print(f"⚠️ Увага: статус логіну {resp.status_code}, відповідь: {resp.text}")


class RentBuilderUser(HttpUser):
    wait_time = between(1, 2)

    @task(3)
    def check_load_balancer(self):
        """Перевірка балансування між репліками (основний маршрут ЛР №6)"""
        self.client.get("/api/server-id")

    @task(2)
    def view_tools(self):
        """Отримання списку інструментів із БД"""
        self.client.get("/tools", headers=SHARED_HEADERS)