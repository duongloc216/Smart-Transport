"""
TrafficFlowObserved Model
Real-time traffic flow observation data
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, DECIMAL
from sqlalchemy.sql import func
from app.core.database import Base


class TrafficFlowObserved(Base):
    __tablename__ = "TrafficFlowObserved"
    
    # Primary Key
    id = Column(String(255), primary_key=True)
    
    # Observed Data
    dateObserved = Column(String(100))
    dateObservedFrom = Column(DateTime, index=True)
    dateObservedTo = Column(DateTime)
    
    # Traffic Metrics - IMPORTANT for ML
    intensity = Column(DECIMAL(18, 2))  # Number of vehicles
    averageVehicleSpeed = Column(DECIMAL(10, 2))  # km/h - TARGET VARIABLE
    occupancy = Column(DECIMAL(5, 4))  # 0-1 ratio
    averageGapDistance = Column(DECIMAL(10, 2))  # meters
    averageHeadwayTime = Column(DECIMAL(10, 2))  # seconds
    averageVehicleLength = Column(DECIMAL(10, 2))  # meters
    
    # Lane Information
    laneId = Column(Integer)
    laneDirection = Column(String(20))  # 'forward', 'backward'
    reversedLane = Column(Boolean)
    
    # Vehicle Type
    vehicleType = Column(String(50))  # 'car', 'bus', 'truck', etc.
    vehicleSubType = Column(String(100))
    
    # Status
    congested = Column(Boolean)
    
    # References - IMPORTANT for joining with RoadSegment
    refRoadSegment = Column(String(255), index=True)  # FK to RoadSegment
    
    # Location (GeoJSON)
    location = Column(Text)  # GeoJSON Point
    address = Column(Text)  # JSON
    
    # Metadata
    name = Column(String(255))
    alternateName = Column(String(255))
    description = Column(Text)
    areaServed = Column(String(255))
    
    # Provenance
    dataProvider = Column(String(255))
    source = Column(String(255))
    owner = Column(Text)  # JSON
    seeAlso = Column(Text)  # JSON
    
    # Timestamps
    dateCreated = Column(DateTime, default=func.now())
    dateModified = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<TrafficFlow(id={self.id}, segment={self.refRoadSegment}, speed={self.averageVehicleSpeed})>"
