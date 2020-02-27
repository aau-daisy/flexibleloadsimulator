from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash
from flask_security import UserMixin

from app.data.database import Base


class User(Base, UserMixin):
    __tablename__ = "user"

    id = Column('id', Integer, primary_key=True, nullable=False, autoincrement=True)
    username = Column('username', String(400), nullable=False, unique=True)
    pwd_hash = Column('pwd_hash', String(4000), nullable=False)
    first_name = Column('first_name', String(400))
    last_name = Column('last_name', String(400))
    email = Column('email', String(400), unique=True, nullable=False)
    max_devices = Column('max_devices', Integer)

    roles = relationship(
        'Role',
        secondary='roles_users',
        backref=backref('user', lazy="raise")
    )

    # Using delete-orphan cascade on a many-to-one or one-to-one requires an additional flag relationship.single_parent
    #  which invokes an assertion that this related object is not to shared with any other parent simultaneously:
    # additional options:   backref='user', lazy='selectin'
    devices = relationship(
        "Device",
        cascade="all, delete, delete-orphan",
        backref="user",
        primaryjoin="User.id==Device.user_id", lazy="dynamic"
    )

    def __init__(self, username, password, first_name, last_name, email, max_devices=10):
        self.username = username
        self.set_password(password)
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.max_devices = max_devices  # TODO: read from pars
        self.devices = []
        self.roles = []

    def set_password(self, password):
        self.pwd_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pwd_hash, password)

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "roles": [role.serialize() for role in self.roles],
            "no_of_devices": self.devices.count(),
            "max_devices": self.max_devices,
            "devices": [device.serialize() for device in self.devices]
            if 0 < self.devices.count() < 5 else ["total {} devices".format(self.devices.count())]
        }

    def __repr__(self):
        return "<%s(username='%s', first_name='%s', last_name='%s', email='%s', max_devices='%s')>" \
               % (self.__class__.__name__, self.username, self.first_name, self.last_name,
                  self.email, self.max_devices)
