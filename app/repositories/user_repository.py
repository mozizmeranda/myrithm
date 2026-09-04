from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.errors import AppException

class UserRepository:
    def get_by_id(self, db: Session, user_id: str) -> Optional[User]:
        return db.scalar(select(User).where(User.id == user_id))

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        norm_email = email.lower().strip()
        return db.scalar(select(User).where(User.email == norm_email))

    def create(self, db: Session, email: str, password_hash: str, role: str = "user") -> User:
        norm_email = email.lower().strip()
        try:
            user = User(
                email=norm_email,
                password_hash=password_hash,
                role=role
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except IntegrityError as e:
            db.rollback()
            raise AppException("DUPLICATE_EMAIL", "Email is already registered", 409) from e

    def update_password(self, db: Session, user_id: str, new_password_hash: str) -> User:
        user = self.get_by_id(db, user_id)
        if not user:
            raise AppException("UNAUTHORIZED", "User not found", 401)
        user.password_hash = new_password_hash
        db.commit()
        db.refresh(user)
        return user

    def count(self, db: Session) -> int:
        return db.scalar(select(func.count(User.id))) or 0
