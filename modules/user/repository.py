from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from models.user import User


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, user_id: UUID) -> User | None:
        """Find a user by their ID."""
        return self.session.scalars(
            select(User).where(User.id == user_id)
        ).first()

    def find_by_email(self, email: str) -> User | None:
        """Find a user by their email address."""
        return self.session.scalars(
            select(User).where(User.email == email)
        ).first()

    def find_by_id_with_orders(self, user_id: UUID) -> User | None:
        """Find a user by ID, eagerly loading their orders to avoid N+1 queries."""
        return self.session.scalars(
            select(User)
            .options(selectinload(User.orders))
            .where(User.id == user_id)
        ).first()

    def find_all(self) -> list[User]:
        """Return all users."""
        return list(self.session.scalars(select(User)).all())

    def create(self, user: User) -> User:
        """Persist a new user and return it with generated fields populated."""
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def update(self, user: User) -> User:
        """Commit changes to an existing user and return the refreshed instance."""
        self.session.commit()
        self.session.refresh(user)
        return user

    def delete(self, user: User) -> None:
        """Delete a user from the database."""
        self.session.delete(user)
        self.session.commit()
