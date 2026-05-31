import os

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

import models  # noqa: F401 — registers all models with Base.metadata
from core.db.base import Base
from core.db.session import get_db
from main import app

_DATABASE_URL = (
    os.getenv("STAGING_DATABASE_URL")
    or os.getenv("TEST_DATABASE_URL")
    or os.getenv("DATABASE_URL")
)
_engine = create_engine(_DATABASE_URL)
_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    """Ensure all tables exist before the test session.

    Uses create_all with checkfirst=True (the default), so existing tables on
    the staging branch are left untouched. Tables are never dropped — the
    staging branch is persistent and shared; only row-level cleanup is done
    between tests via clean_tables.
    """
    Base.metadata.create_all(bind=_engine)
    yield


@pytest.fixture
def db_session(create_tables):
    """Provide a database session for a single test."""
    session = _SessionLocal()
    yield session
    session.close()


@pytest.fixture(autouse=True)
def clean_tables(db_session):
    """Delete all rows between tests respecting foreign key order.

    The rollback at the start of teardown resets any broken transaction state
    caused by a test failure (e.g. IntegrityError), so cleanup can always run.
    """
    yield
    db_session.rollback()
    db_session.execute(text("DELETE FROM payment"))
    db_session.execute(text("DELETE FROM order_item"))
    db_session.execute(text('DELETE FROM "order"'))
    db_session.execute(text("DELETE FROM cart_item"))
    db_session.execute(text("DELETE FROM cart"))
    db_session.execute(text("DELETE FROM product"))
    db_session.execute(text("DELETE FROM category"))
    db_session.execute(text('DELETE FROM "user"'))
    db_session.commit()


@pytest.fixture
def client(db_session):
    """Provide a TestClient with get_db overridden to use the test session."""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── Payload factories ─────────────────────────────────────────────────────────

@pytest.fixture
def user_payload():
    """Return a valid user creation payload."""
    return {"name": "Test User", "email": "test@example.com", "password": "senha123"}


@pytest.fixture
def category_payload():
    """Return a valid category creation payload."""
    return {"name": "Electronics"}


@pytest.fixture
def product_payload(sample_category):
    """Return a valid product creation payload referencing an existing category."""
    return {
        "category_id": sample_category["id"],
        "name": "Laptop",
        "description": "A powerful test laptop",
        "price": 999.99,
        "quantity_available": 10,
    }


# ── Created entity fixtures ───────────────────────────────────────────────────

@pytest.fixture
def sample_user(client, user_payload):
    """Create and return a user via the API."""
    return client.post("/users/", json=user_payload).json()


@pytest.fixture
def sample_category(client, category_payload):
    """Create and return a category via the API."""
    return client.post("/categories/", json=category_payload).json()


@pytest.fixture
def sample_product(client, product_payload):
    """Create and return a product via the API."""
    return client.post("/products/", json=product_payload).json()


@pytest.fixture
def cart_with_item(client, sample_user, sample_product):
    """Create a cart with one item and return it."""
    client.post(
        f"/cart/{sample_user['id']}/items",
        json={"product_id": sample_product["id"], "quantity": 2},
    )
    return client.get(f"/cart/{sample_user['id']}").json()
