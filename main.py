from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import models
import schemas
import auth
from database import engine, get_db
from repositories import UserRepository, TaskRepository

app = FastAPI(
    title="Task Management System API",
    description="A secure task management service featuring complete CRUD operations for user workflows, secured via JWT token-based authentication.",
    version="1.0.0"
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Async DB initialization on startup
@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

# Current user dependency
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = auth.decode_access_token(token)
    if payload is None:
        raise credentials_exception
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    user_repo = UserRepository(db)
    user = await user_repo.get_by_username(username)
    if user is None:
        raise credentials_exception
    return user

# ROOT
@app.get("/", tags=["General"])
async def read_root():
    return {
        "message": "Welcome to the Task Management System API (Async Postgres)",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# AUTH ENDPOINTS
@app.post("/auth/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED, tags=["Authentication"])
async def register(user_data: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    db_user = await user_repo.get_by_username(user_data.username)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username is already registered")
    
    hashed_password = auth.get_password_hash(user_data.password)
    user = await user_repo.create(username=user_data.username, password_hash=hashed_password)
    return user

@app.post("/auth/login", response_model=schemas.Token, tags=["Authentication"])
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    user = await user_repo.get_by_username(form_data.username)
    if not user or not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# TASKS ENDPOINTS
@app.post("/tasks", response_model=schemas.TaskResponse, status_code=status.HTTP_201_CREATED, tags=["Tasks"])
async def create_task(task_data: schemas.TaskCreate, current_user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    task_repo = TaskRepository(db)
    return await task_repo.create(task=task_data, owner_id=current_user.id)

@app.get("/tasks", response_model=List[schemas.TaskResponse], tags=["Tasks"])
async def get_tasks(current_user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    task_repo = TaskRepository(db)
    return await task_repo.get_all_by_owner(owner_id=current_user.id)

@app.get("/tasks/{task_id}", response_model=schemas.TaskResponse, tags=["Tasks"])
async def get_task(task_id: int, current_user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    task_repo = TaskRepository(db)
    task = await task_repo.get_by_id(task_id=task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if task.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this task")
    return task

@app.put("/tasks/{task_id}", response_model=schemas.TaskResponse, tags=["Tasks"])
async def update_task(task_id: int, task_update: schemas.TaskUpdate, current_user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    task_repo = TaskRepository(db)
    task = await task_repo.get_by_id(task_id=task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if task.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this task")
    
    return await task_repo.update(db_task=task, task_update=task_update)

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Tasks"])
async def delete_task(task_id: int, current_user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    task_repo = TaskRepository(db)
    task = await task_repo.get_by_id(task_id=task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if task.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this task")
    
    await task_repo.delete(db_task=task)
    return None
