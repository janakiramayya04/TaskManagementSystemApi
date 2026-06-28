from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
import models
import schemas

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> Optional[models.User]:
        result = await self.db.execute(select(models.User).filter(models.User.id == user_id))
        return result.scalars().first()

    async def get_by_username(self, username: str) -> Optional[models.User]:
        result = await self.db.execute(select(models.User).filter(models.User.username == username))
        return result.scalars().first()

    async def create(self, username: str, password_hash: str) -> models.User:
        db_user = models.User(username=username, password_hash=password_hash)
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

class TaskRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, task_id: int) -> Optional[models.Task]:
        result = await self.db.execute(select(models.Task).filter(models.Task.id == task_id))
        return result.scalars().first()

    async def get_all_by_owner(self, owner_id: int) -> List[models.Task]:
        result = await self.db.execute(select(models.Task).filter(models.Task.owner_id == owner_id))
        return result.scalars().all()

    async def create(self, task: schemas.TaskCreate, owner_id: int) -> models.Task:
        db_task = models.Task(
            title=task.title,
            description=task.description,
            status=task.status,
            owner_id=owner_id
        )
        self.db.add(db_task)
        await self.db.commit()
        await self.db.refresh(db_task)
        return db_task

    async def update(self, db_task: models.Task, task_update: schemas.TaskUpdate) -> models.Task:
        update_data = task_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_task, key, value)
        await self.db.commit()
        await self.db.refresh(db_task)
        return db_task

    async def delete(self, db_task: models.Task) -> None:
        await self.db.delete(db_task)
        await self.db.commit()
