import datetime
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


class ReadRecording(BaseModel):
    id: int
    starttime: datetime.datetime
    endtime: datetime.datetime 
    camera_id: int 

    class Config:
        orm_mode = True

class CreateRecording(BaseModel):
    starttime: datetime.datetime
    endtime: datetime.datetime 
    camera_id: int 


class Camera(BaseModel):
    id: int
    name: str
    description: str
    ipaddress: str
    zone_id: int
    recordings: list[ReadRecording] = []

    class Config:
        orm_mode = True

class ReadZone(BaseModel):
    id: int
    title: str
    description: str
    plant_id: int
    #assignee_id: int
    cameras: list[Camera] = []

    class Config:
        orm_mode = True

class CreateZone(BaseModel):
    title: str
    description: str
    plant_id: int
    assignee_id: int
    cameras: list[Camera] = []

    class Config:
        orm_mode = True



    
class Scenario(BaseModel):
    id: int 
    name: str
    description: str 

    class Config:
        orm_mode = True


class Plant(BaseModel):
    id: int
    name: str
    description: str
    address: str 
    zones : list[ReadZone] = []

    class Config:
        orm_mode = True

class ReadPlant(BaseModel):
    id: int
    name: str
    description: str
    address: str
    zones : list[ReadZone] 

    class Config:
        orm_mode = True

class CreatePlant(BaseModel):
    name: str
    description: str
    address: str 

    class Config:
        orm_mode = True

