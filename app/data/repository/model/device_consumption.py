from sqlalchemy import Column, Integer, Float, Boolean, DateTime, ForeignKey

from app.data.database import Base


class DeviceConsumption(Base):
    __tablename__ = "device_consumption"

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    power = Column('power', Float)
    energy = Column('energy', Float)
    status = Column('state', Boolean)
    timestamp = Column('timestamp', DateTime)
    device_id = Column('device_id', Integer, ForeignKey("device.id"), nullable=False)

    def __init__(self, power, energy, status, timestamp):
        self.power = power
        self.energy = energy
        self.status = status
        self.timestamp = timestamp

    def serialize(self):
        return {
            "power": self.power,
            "energy": self.energy,
            "status": self.status,
            "timestamp": self.timestamp
        }

    def __repr__(self):
        return "<%s(power='%s', energy='%s', status='%s', device_id='%s', timestamp='%s')>" % (
            self.__class__.__name__, self.power, self.energy, self.status, self.device_id, self.timestamp)
