import json
import socket
from typing import List, Optional

import redis
from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.api.deps import get_current_admin, get_current_user
from src.config import settings
from src.core.security import create_access_token, get_password_hash, verify_password
from src.db.database import Base, engine, get_db
from src.models.tool import Tool
from src.models.user import Role, User
from src.schemas.tool import ToolCreate, ToolResponse
from src.schemas.user import UserCreate, UserResponse

# Створюємо таблиці в БД
Base.metadata.create_all(bind=engine)

app = FastAPI(debug=settings.DEBUG)

# Підключення до Redis для кешування важких вибірок
redis_client = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)
CACHE_TTL_SECONDS = 60


# Middleware: додає заголовок X-Server-ID до кожної відповіді сервера
@app.middleware("http")
async def add_server_id_header(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Server-ID"] = socket.gethostname()
    return response


# Тестовий маршрут: повертає ID екземпляра в JSON-відповіді
@app.get("/api/server-id")
def get_server_id():
    return {
        "status": "healthy",
        "server_id": socket.gethostname(),
    }


@app.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")

    role = Role.admin if "admin" in user_in.email else Role.user

    new_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        role=role,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/dashboard/user")
def user_dashboard(current_user: User = Depends(get_current_user)):
    return {
        "message": "Welcome to User Dashboard",
        "user_email": current_user.email,
        "role": current_user.role,
    }


@app.get("/dashboard/admin")
def admin_dashboard(current_admin: User = Depends(get_current_admin)):
    return {
        "message": "Welcome to Admin Control Panel",
        "admin_email": current_admin.email,
        "permissions": "all_access",
    }


@app.post("/tools", response_model=ToolResponse)
def create_tool(
    tool_in: ToolCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    new_tool = Tool(
        name=tool_in.name,
        description=tool_in.description,
        price_per_day=tool_in.price_per_day,
        owner_id=current_admin.id,
    )
    db.add(new_tool)
    db.commit()
    db.refresh(new_tool)

    # Інвалідація кешу після додавання нового інструмента
    try:
        for key in redis_client.scan_iter("tools_cache:*"):
            redis_client.delete(key)
    except redis.RedisError:
        pass

    return new_tool


@app.get("/tools", response_model=List[ToolResponse])
def get_tools(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cache_key = f"tools_cache:{skip}:{limit}:{min_price}:{max_price}"

    # 1. Перевіряємо наявність даних у Redis (Cache Hit)
    try:
        cached_data = redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
    except redis.RedisError:
        pass

    # 2. Якщо в кеші порожньо  робимо оптимізований запит із індексом та пагінацією
    query = db.query(Tool).filter(Tool.is_available.is_(True))
    if min_price is not None:
        query = query.filter(Tool.price_per_day >= min_price)
    if max_price is not None:
        query = query.filter(Tool.price_per_day <= max_price)

    tools = query.offset(skip).limit(limit).all()

    # 3. Зберігаємо результат у Redis із TTL = 60 секунд
    try:
        serialized = [
            ToolResponse.model_validate(t).model_dump() for t in tools
        ]
        redis_client.setex(cache_key, CACHE_TTL_SECONDS, json.dumps(serialized))
    except redis.RedisError:
        pass

    return tools


@app.get("/")
def read_root():
    return {"message": "Hello from Docker with Hot-Reload!"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if settings.DEBUG:
        return JSONResponse(
            status_code=500,
            content={"message": "Internal Server Error", "details": str(exc)},
        )

    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error. Please contact support."},
    )