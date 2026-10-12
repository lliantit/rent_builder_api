from locust import HttpUser, between, task


class RentBuilderUser(HttpUser):
    # Імітація реального користувача: затримка між кліками від 1 до 3 секунд
    wait_time = between(1, 3)

    def on_start(self):
        """Цей метод виконується один раз"""

        # ВАЖЛИВО: Вкажи тут email та пароль реального користувача з твоєї бази!
        response = self.client.post(
            "/login", data={"username": "admin1@mail.com", "password": "testpassword"}
        )

        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            print("Помилка логіну! Перевір email та пароль у locustfile.py")
            self.headers = {}

    @task(3)
    def view_tools(self):
        """Імітуємо перегляд списку інструментів (виконується частіше, вага 3)"""
        if self.headers:
            self.client.get("/tools", headers=self.headers)

    @task(1)
    def view_dashboard(self):
        """Імітуємо захід у профайл (виконується рідше, вага 1)"""
        if self.headers:
            self.client.get("/dashboard/user", headers=self.headers)
