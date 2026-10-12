from fastapi.testclient import TestClient

from src.main import app

# Створюємо клієнта для симуляції запитів до нашого API
client = TestClient(app)


def test_register_user():
    response = client.post(
        "/register", json={"email": "pytest_user@mail.com", "password": "testpassword"}
    )
    # Перевіряємо, чи повернувся успішний статус
    assert response.status_code == 200
    # Перевіряємо, чи правильно збереглася пошта
    assert response.json()["email"] == "pytest_user@mail.com"
    # Перевіряємо, чи видано роль звичайного юзера
    assert response.json()["role"] == "user"


def test_login_user():
    response = client.post(
        "/login", data={"username": "pytest_user@mail.com", "password": "testpassword"}
    )
    # Перевіряємо статус логіну
    assert response.status_code == 200
    # Перевіряємо, чи видав сервер токен доступу
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
