import datetime
from sqlalchemy import UUID, Boolean, Column, DateTime, Float, ForeignKey, Integer, LargeBinary, String, TIMESTAMP
from sqlalchemy.orm import relationship

from .database import Base


class Plant(Base):
    __tablename__ = "plants"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    description = Column(String(100))
    address = Column(String(100))
    plantConfidence = Column(Float)

    zones = relationship("Zone", back_populates="plant")


class Assignee(Base):
    __tablename__ = "assignees"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), index=True)
    email = Column(String(100))
    phone = Column(String(100))
    
    assignee = relationship("Zone", back_populates="assignees")

class ZoneScenario(Base):
    __tablename__ = "zone_scenarios"

    id = Column(Integer, primary_key=True)

    zoneid = Column(Integer)
    scenarioid = Column(Integer)


class Zone(Base):
    __tablename__ = "zones"

    id = Column(Integer, primary_key=True)
    title = Column(String(100), index=True)
    description = Column(String(100))
    zoneconfidence = Column(Float)
    plant_id = Column(Integer, ForeignKey("plants.id"))
    assignee_id = Column(Integer, ForeignKey("assignees.id"))

    plant = relationship("Plant", back_populates="zones")
    cameras = relationship("Camera", back_populates="zone")
    assignees = relationship("Assignee", back_populates="assignee")


class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), index=True)
    description = Column(String(100))
    ipaddress = Column(String(100))
    zone_id = Column(Integer, ForeignKey("zones.id"))

    zone = relationship("Zone", back_populates="cameras")
    recordings = relationship("Recording", back_populates="camera")


class Recording(Base):
    __tablename__ = "recordings"

    id = Column(Integer, primary_key=True)
    starttime = Column(TIMESTAMP)
    endtime = Column(TIMESTAMP)
    status = Column(Boolean, unique=False, default=True)
    task_id = Column(String(256))
    camera_id = Column(Integer, ForeignKey("cameras.id"))

    camera = relationship("Camera", back_populates="recordings")
    incidents = relationship("Incident", back_populates="recording")


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    class_name = Column(String(256), index=True)
    confidence = Column(Float)
    bbox = Column(String(256))
    frame = Column(LargeBinary(length=(2**32)-1))
    recording_id = Column(Integer, ForeignKey("recordings.id"))

    recording = relationship("Recording", back_populates="incidents")


class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), index=True)
    description = Column(String(100))
    
