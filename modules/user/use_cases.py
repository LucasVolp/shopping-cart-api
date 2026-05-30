from uuid import UUID

from core.security import hash_password
from models.user import User
from modules.user.dto import CreateUserDTO, UpdateUserDTO
from modules.user.repository import UserRepository


class UserUseCases:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def get_by_id(self, user_id: UUID) -> User:
        """Return a user by ID or raise ValueError if not found."""
        user = self.repository.find_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        return user

    def get_by_id_with_orders(self, user_id: UUID) -> User:
        """Return a user with their full order history or raise ValueError if not found."""
        user = self.repository.find_by_id_with_orders(user_id)
        if not user:
            raise ValueError("User not found")
        return user

    def get_all(self) -> list[User]:
        """Return all registered users."""
        return self.repository.find_all()

    def create(self, dto: CreateUserDTO) -> User:
        """Create a new user, hashing the password before persisting.

        Raises ValueError if the email is already registered.
        """
        if self.repository.find_by_email(dto.email):
            raise ValueError("Email already in use")
        user = User(
            name=dto.name,
            email=dto.email,
            password=hash_password(dto.password),
        )
        return self.repository.create(user)

    def update(self, user_id: UUID, dto: UpdateUserDTO) -> User:
        """Update a user's name or email.

        Only fields explicitly provided in the DTO are changed.
        Raises ValueError if the user is not found or if the new email is taken.
        """
        user = self.get_by_id(user_id)
        if dto.name is not None:
            user.name = dto.name
        if dto.email is not None:
            if self.repository.find_by_email(dto.email):
                raise ValueError("Email already in use")
            user.email = dto.email
        return self.repository.update(user)

    def delete(self, user_id: UUID) -> None:
        """Delete a user by ID or raise ValueError if not found."""
        user = self.get_by_id(user_id)
        self.repository.delete(user)
