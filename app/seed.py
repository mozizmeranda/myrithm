import logging
from sqlalchemy.orm import Session
from app.database import engine, init_db, SessionLocal
from app.models.stream import Stream

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

INITIAL_STREAMS = [
    {"id": "cardio", "title": "Кардио", "description": "Динамичная интервальная кардио-тренировка", "is_active": True},
    {"id": "back", "title": "Здоровая спина", "description": "Короткий комплекс для осанки и расслабления спины", "is_active": False},
    {"id": "office", "title": "Офисная разминка", "description": "Быстрые упражнения прямо на рабочем месте", "is_active": False},
    {"id": "dance", "title": "Танцевальный ритм", "description": "Зажигательная ритмичная тренировка", "is_active": False},
    {"id": "60plus", "title": "60+ Мягкий ритм", "description": "Мягкая суставная гимнастика и активное долголетие", "is_active": False},
]

def seed_streams():
    logger.info("Initializing database schema...")
    init_db()

    session: Session = SessionLocal()
    try:
        count_created = 0
        for s_data in INITIAL_STREAMS:
            existing = session.get(Stream, s_data["id"])
            if not existing:
                stream = Stream(
                    id=s_data["id"],
                    title=s_data["title"],
                    description=s_data["description"],
                    is_active=s_data["is_active"]
                )
                session.add(stream)
                count_created += 1
        
        session.commit()
        logger.info(f"Seeding completed. Created {count_created} new streams.")
    except Exception as e:
        session.rollback()
        logger.error(f"Error during seeding: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    seed_streams()

