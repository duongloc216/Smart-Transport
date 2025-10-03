"""
RoadAccident Model
Traffic accident records for routing avoidance
"""

from sqlalchemy import Column, String, Integer, Text, DateTime, DECIMAL, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class RoadAccident(Base):
    __tablename__ = "RoadAccident"
    
    # Primary Key
    id = Column(String(255), primary_key=True)
    localId = Column(String(100))
    
    # Accident Date & Time
    accidentDate = Column(DateTime, index=True)
    accidentStatisticalDate = Column(Text)  # JSON
    
    # Accident Details
    accidentType = Column(Text)  # JSON
    accidentDescription = Column(Text)  # JSON
    accidentLocation = Column(String(50))  # Enum value
    
    # Location - IMPORTANT for routing
    location = Column(Text)  # GeoJSON Point
    
    # Road Information
    roadClass = Column(String(100), index=True)
    roadIntersection = Column(String(50))
    roadPaving = Column(String(50))
    roadSign = Column(String(50))
    roadSurface = Column(String(50))
    roadTrunk = Column(String(50))
    
    # Casualties
    numPassengersDead = Column(Integer, default=0)
    numPassengersInjured = Column(Integer, default=0)
    numPedestrianDead = Column(Integer, default=0)
    numPedestrianInjured = Column(Integer, default=0)
    totalDeadPeopleWithin24Hours = Column(Integer, default=0)
    totalDeadPeopleWithin30Days = Column(Integer, default=0)
    totalInjured = Column(Integer, default=0)
    
    # Involved Parties
    pedestriansInvolved = Column(Boolean)
    vehiclesInvolved = Column(Text)  # JSON
    weakestSubject = Column(String(50))
    
    # Weather Conditions
    weatherConditions = Column(Text)  # JSON
    
    # Status - IMPORTANT for routing
    status = Column(String(50), index=True)  # 'onGoing', 'solved', 'archived'
    
    # Metadata
    name = Column(String(255))
    alternateName = Column(String(255))
    description = Column(Text)
    areaServed = Column(String(255))
    address = Column(Text)  # JSON
    
    # Provenance
    dataProvider = Column(String(255))
    source = Column(String(255))
    owner = Column(Text)  # JSON
    seeAlso = Column(Text)  # JSON
    
    # Timestamps
    dateCreated = Column(DateTime, default=func.now())
    dateModified = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<RoadAccident(id={self.id}, status={self.status}, date={self.accidentDate})>"
