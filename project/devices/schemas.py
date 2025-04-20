from pydantic import BaseModel
from enum import Enum

class MeasurementCreate(BaseModel):
    """Схема для создания нового измерения"""
    device_id: int
    x: float
    y: float
    z: float

class MeasurementAxis(str, Enum):
    """Оси измерения для документации API"""
    X = 'x'
    Y = 'y'
    Z = 'z'

class StatsResponse(BaseModel):
    """Схема ответа со статистикой"""
    axis: MeasurementAxis
    min: float
    max: float
    count: int
    sum: float
    median: float 

class DeviceStatsResponse(BaseModel):
    """Схема ответа со статистикой по устройству"""
    device_id: int 
    stats: dict[MeasurementAxis, StatsResponse]