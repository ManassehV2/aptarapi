import datetime
from typing import Optional
from pydantic import BaseModel


class Incident(BaseModel):
    id: int 
    timestamp: datetime.date
    class_name: str
    confidence: str
    bbox: str
    frame: str
    recording_id: int

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class ReadRecording(BaseModel):
    id: int
    starttime: datetime.datetime
    endtime: Optional[datetime.datetime]
    status: bool
    task_id: Optional[str] 
    camera_id: int 

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class CreateRecording(BaseModel):
    starttime: datetime.datetime
    endtime: Optional[datetime.datetime] = None
    status: bool = True
    task_id: Optional[str] = None  
    camera_id: int 
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class Camera(BaseModel):
    id: int
    name: str
    description: str
    ipaddress: str
    zone_id: int
    recordings: list[ReadRecording] = []

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class ReadCamera(BaseModel):
    id: int
    name: str
    description: str
    ipaddress: str
    zone_id: int
    recordings: list[ReadRecording] = []

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class CreateCamera(BaseModel):
    name: str
    description: str
    ipaddress: str
    zone_id: int

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class CreateZoneCamera(BaseModel):
    name: str
    description: str
    ipaddress: str
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
class ReadZone(BaseModel):
    id: int
    title: str
    description: str
    plant_id: int
    assignee_id: int
    zoneconfidence: Optional[float]
    cameras: list[Camera] = []

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class CreateZone(BaseModel):
    title: str
    description: str
    plant_id: int
    zoneconfidence: Optional[float]
    assignee_id: int
    cameras: list[CreateZoneCamera] = []

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True



    
class Scenario(BaseModel):
    id: int 
    name: str
    description: str 

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class ReadScenario(BaseModel):
    id: int 
    name: str
    description: Optional[str] 

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class CreateScenario(BaseModel):
    name: str
    description: Optional[str] 

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class Plant(BaseModel):
    id: int
    name: str
    description: str
    address: str
    plantConfidence: float 
    zones : list[ReadZone] = []

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class ReadPlant(BaseModel):
    id: int
    name: str
    description: str
    address: str
    plantConfidence: float
    zones : list[ReadZone] 

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class CreatePlant(BaseModel):
    name: str
    description: str
    address: str
    plantConfidence: float

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

