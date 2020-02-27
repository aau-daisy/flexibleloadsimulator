from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.data.database import Base


class DeviceModel(Base):
    __tablename__ = "device_model"

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    model_name = Column('model_name', String(200))
    params = Column('params', JSON)

    # one-to-one relationship with Device
    device_id = Column(Integer, ForeignKey('device.id'))
    device = relationship("Device", back_populates='device_model')

    def __init__(self, model_name, params):
        self.model_name = model_name
        self.params = params

    def serialize(self):
        return {
            "model_name": self.model_name,
            "params": self.params,
        }

    def __repr__(self):
        return "<%s(model_name='%s', params='%s')>"\
               % (self.__class__.__name__, self.model_name, self.params)
