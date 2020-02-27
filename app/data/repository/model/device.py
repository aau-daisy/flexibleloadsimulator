from sqlalchemy import Column, String, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
import uuid

from app.data.database import Base
from app.data.model.device_type_enum import DeviceTypeEnum


class Device(Base):
    __tablename__ = "device"

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    device_name = Column('device_name', String(200))
    device_id = Column('device_id', String(100))
    device_state = Column('power_state', Enum(DeviceTypeEnum), default=DeviceTypeEnum.INACTIVE)

    # below attributes are relationships with other tables
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    consumption = relationship('DeviceConsumption', cascade="all, delete, delete-orphan", backref="device",
                               primaryjoin="Device.id==DeviceConsumption.device_id", lazy="dynamic")

    device_model = relationship('DeviceModel', uselist=False, back_populates="device")

    def __init__(self, device_name):
        self.device_id = uuid.uuid4().hex
        self.device_name = device_name
        self.device_state = DeviceTypeEnum.INACTIVE
        self.consumption = []

    def serialize(self):
        return {
            "id": self.id,
            "device_name": self.device_name,
            "device_id": self.device_id,
            "device_state": self.device_state.value,
            "user_id": self.user_id,
            "device_model": self.device_model.serialize() if self.device_model is not None else None
        }

    def __repr__(self):
        return "<%s(device_name='%s', device_id='%s', device_state='%s', user_id='%s')>" \
               % (self.__class__.__name__, self.device_name, self.device_id, self.device_state.value, self.user_id)
