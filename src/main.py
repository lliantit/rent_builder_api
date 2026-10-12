from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request, status
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

app = FastAPI(debug=settings.DEBUG)

# Створюємо таблиці в БД
Base.metadata.create_all(bind=engine)

app = FastAPI(debug=settings.DEBUG)


@app.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # якщо email містить слово admin, даємо права адміністратора
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
    # OAuth2PasswordRequestForm використовує поле username, ми туди передаємо email
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


# Сторінка доступна для всіх авторизованих користувачів
@app.get("/dashboard/user")
def user_dashboard(current_user: User = Depends(get_current_user)):
    return {
        "message": "Welcome to User Dashboard",
        "user_email": current_user.email,
        "role": current_user.role,
    }


# Сторінка доступна ТІЛЬКИ для адміністраторів
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
    return new_tool


@app.get("/tools", response_model=List[ToolResponse])
def get_tools(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    tools = db.query(Tool).all()
    return tools


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if settings.DEBUG:
        # У режимі sandbox (DEBUG=True) показуємо деталі помилки розробнику
        return JSONResponse(
            status_code=500,
            content={"message": "Internal Server Error", "details": str(exc)},
        )

    # У режимі production (DEBUG=False) ховаємо стектрейс від користувача
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error. Please contact support."},
    )
