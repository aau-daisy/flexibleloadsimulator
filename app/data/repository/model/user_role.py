from sqlalchemy import Column, String, Integer, ForeignKey, Enum
from flask_security import RoleMixin

from app.data.database import Base
from app.data.model.role_type_enum import RoleTypeEnum


class RolesUsers(Base):
    def __init__(self):
        pass

    __tablename__ = 'roles_users'

    id = Column(Integer(), primary_key=True)
    user_id = Column('user_id', Integer(), ForeignKey('user.id', ondelete='CASCADE'))
    role_id = Column('role_id', Integer(), ForeignKey('role.id', ondelete='CASCADE'))


class Role(Base, RoleMixin):
    __tablename__ = 'role'
    id = Column('id', Integer(), primary_key=True)
    name = Column('name', Enum(RoleTypeEnum), unique=True)
    description = Column('description', String(255))

    def serialize(self):
        return {
            "name": self.name.value,
            "description": self.description
        }
