import pytest
import concurrent.futures
from pathlib import Path
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.user import User
from app.models.stream import Stream
from app.models.activity import ActivityLog
from app.models.lead import StreamLead
from app.services.auth_service import AuthService
from app.services.activity_service import ActivityService
from app.services.lead_service import LeadService
from app.schemas.auth import RegisterRequest
from app.schemas.activity import ActivitySyncRequest
from app.schemas.lead import LeadCreateRequest
from app.create_admin import create_admin
from app.errors import AppException

CONCURRENCY_DB_PATH = Path("./data/concurrency_test.db")
CONCURRENCY_DB_URL = f"sqlite:///{CONCURRENCY_DB_PATH}"

engine = create_engine(
    CONCURRENCY_DB_URL,
    connect_args={"check_same_thread": False},
    pool_size=10,
    max_overflow=20
)

# Listeners for WAL mode and busy timeout
from sqlalchemy import event
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute("PRAGMA busy_timeout=5000;")
    cursor.close()

SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module", autouse=True)
def setup_concurrency_db():
    CONCURRENCY_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if CONCURRENCY_DB_PATH.exists():
        try:
            CONCURRENCY_DB_PATH.unlink()
        except Exception:
            pass

    Base.metadata.create_all(bind=engine)
    
    # Seed active stream
    session = SessionFactory()
    stream = Stream(id="cardio_conc", title="Concurrency Cardio", is_active=True)
    session.add(stream)
    session.commit()
    session.close()

    yield

    engine.dispose()
    if CONCURRENCY_DB_PATH.exists():
        try:
            CONCURRENCY_DB_PATH.unlink()
        except Exception:
            pass

def test_concurrent_registration():
    email = "concurrent_reg@example.com"
    password = "Password123!"
    auth_service = AuthService()

    def register_worker(worker_id):
        session = SessionFactory()
        try:
            res = auth_service.register(session, email, password)
            session.close()
            return ("SUCCESS", 201)
        except AppException as e:
            session.close()
            return ("ERROR", e.status_code, e.code)
        except Exception as e:
            session.close()
            return ("EXCEPTION", str(e))

    num_threads = 5
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(register_worker, i) for i in range(num_threads)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    successes = [r for r in results if r[0] == "SUCCESS"]
    conflicts = [r for r in results if r[0] == "ERROR" and r[1] == 409]

    assert len(successes) == 1, f"Expected 1 success, got {len(successes)}. Results: {results}"
    assert len(conflicts) == num_threads - 1

    # Verify only 1 user exists in DB
    session = SessionFactory()
    user_count = session.scalar(select(func.count(User.id)).where(User.email == email))
    session.close()
    assert user_count == 1

def test_concurrent_admin_creation():
    def create_admin_worker():
        session = SessionFactory()
        try:
            # We override session in create_admin or call logic with SessionFactory
            from app.security import hash_password
            existing = session.scalar(select(User).where(User.role == "admin"))
            if existing:
                session.close()
                return "EXISTS"
            admin_user = User(email="admin_conc@example.com", password_hash=hash_password("Pass123!"), role="admin")
            session.add(admin_user)
            session.commit()
            session.close()
            return "CREATED"
        except Exception as e:
            session.rollback()
            session.close()
            return "DUPLICATE_OR_LOCKED"

    num_threads = 4
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(create_admin_worker) for _ in range(num_threads)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    session = SessionFactory()
    admin_count = session.scalar(select(func.count(User.id)).where(User.role == "admin"))
    session.close()

    assert admin_count == 1

def test_concurrent_activity_sync():
    # Register a user first
    session = SessionFactory()
    auth_service = AuthService()
    user = auth_service.register(session, "activity_user@example.com", "Password123!")
    user_id = user.id
    session.close()

    activity_service = ActivityService()

    def sync_worker(i):
        session = SessionFactory()
        try:
            req = ActivitySyncRequest(stream_id="cardio_conc", duration_seconds=30, estimated_steps=40)
            res = activity_service.sync_activity(session, user_id, req)
            session.close()
            return "SUCCESS"
        except Exception as e:
            session.close()
            return f"ERROR: {e}"

    num_threads = 10
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(sync_worker, i) for i in range(num_threads)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    successes = [r for r in results if r == "SUCCESS"]
    assert len(successes) == num_threads

    session = SessionFactory()
    total_logs = session.scalar(select(func.count(ActivityLog.id)).where(ActivityLog.user_id == user_id))
    session.close()
    assert total_logs == num_threads

def test_concurrent_leads_submission():
    lead_service = LeadService()

    async def run_lead(i):
        session = SessionFactory()
        req = LeadCreateRequest(email=f"lead_{i}@example.com", stream_code="dance")
        res = await lead_service.create_lead(session, req)
        session.close()
        return res

    import asyncio
    async def main_concurrent_leads():
        tasks = [run_lead(i) for i in range(5)]
        return await asyncio.gather(*tasks)

    results = asyncio.run(main_concurrent_leads())
    assert len(results) == 5

    session = SessionFactory()
    total_leads = session.scalar(select(func.count(StreamLead.id)))
    session.close()
    assert total_leads >= 5
