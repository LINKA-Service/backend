from sqlalchemy import Column, Integer, String, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

# User-Server Many-to-Many relationship
user_servers = Table(
    'user_servers',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE')),
    Column('server_id', Integer, ForeignKey('servers.id', ondelete='CASCADE'))
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    display_name = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    servers = relationship("Server", secondary=user_servers, back_populates="members")
    owned_servers = relationship("Server", back_populates="owner")
    messages = relationship("Message", back_populates="author", cascade="all, delete-orphan")
