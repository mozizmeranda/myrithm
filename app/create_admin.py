import logging
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import init_db, SessionLocal
from app.models.user import User
from app.security import hash_password
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_admin():
    init_db()
    session: Session = SessionLocal()
    try:
        admin_email = settings.ADMIN_EMAIL
        admin_password = settings.ADMIN_PASSWORD

        # Check if admin already exists by role
        existing_admin_by_role = session.scalar(select(User).where(User.role == "admin"))
        if existing_admin_by_role:
            logger.info(f"Admin already exists with email: {existing_admin_by_role.email}")
            return

        # Check if user with admin email exists
        existing_user = session.scalar(select(User).where(User.email == admin_email))
        if existing_user:
            logger.info(f"User with email '{admin_email}' exists. Promoting to admin...")
            existing_user.role = "admin"
            existing_user.password_hash = hash_password(admin_password)
            session.commit()
            logger.info("Admin promoted successfully.")
            return

        admin_user = User(
            email=admin_email,
            password_hash=hash_password(admin_password),
            role="admin"
        )
        session.add(admin_user)
        session.commit()
        logger.info(f"Single administrator account successfully created: {admin_email}")
    except IntegrityError as e:
        session.rollback()
        logger.warning(f"Integrity check prevented duplicate admin creation: {e}")
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to create admin: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    create_admin()
