"""
RoadSegment Model
Detailed road segment information for routing
"""

from sqlalchemy import Column, String, Integer, Float, Text, DateTime, DECIMAL
from sqlalchemy.sql import func
from app.core.database import Base


class RoadSegment(Base):
    __tablename__ = "RoadSegment"
    
    # Primary Key
    id = Column(String(255), primary_key=True)
    
    # Segment Identification
    roadId = Column(String(255), index=True)
    roadName = Column(String(255), index=True)
    agency_name = Column(String(255))
    
    # Classification
    roadClass = Column(String(100), index=True)  # Highway classification
    category = Column(Text)  # JSON array
    
    # Location
    location = Column(Text)  # GeoJSON LineString
    startPoint = Column(Text)  # GeoJSON Point
    endPoint = Column(Text)  # GeoJSON Point
    
    # Kilometer Posts
    startKilometer = Column(DECIMAL(10, 3))
    endKilometer = Column(DECIMAL(10, 3))
    
    # Physical Dimensions - IMPORTANT for routing
    length = Column(DECIMAL(15, 2))  # meters
    width = Column(DECIMAL(10, 2))  # meters
    carriagewayLength = Column(DECIMAL(15, 2))
    carriagewayWidth = Column(DECIMAL(10, 2))
    rightOfWayWidth = Column(DECIMAL(10, 2))
    
    # Lane Information - IMPORTANT for capacity
    totalLaneNumber = Column(Integer)
    laneInfo = Column(Text)  # JSON
    laneUsage = Column(Text)  # JSON
    
    # Speed Limits - IMPORTANT for routing
    maximumAllowedSpeed = Column(DECIMAL(10, 2))  # km/h
    minimumAllowedSpeed = Column(DECIMAL(10, 2))  # km/h
    
    # Weight & Size Restrictions
    maximumAllowedHeight = Column(DECIMAL(10, 2))  # meters
    maximumAllowedWeight = Column(DECIMAL(10, 2))  # tons
    maximumAllowedWidth = Column(DECIMAL(10, 2))  # meters
    
    # Allowed Vehicles
    allowedVehicleType = Column(Text)  # JSON
    
    # Road Material
    roadMaterial = Column(String(100))
    
    # Road Direction
    roadDirection = Column(String(50))
    
    # Median
    medianLength = Column(DECIMAL(15, 2))
    medianWidth = Column(DECIMAL(10, 2))
    medianHeight = Column(DECIMAL(10, 2))
    
    # Cycle Path
    cyclePathPlacement = Column(String(50))
    cyclePathLeftWidth = Column(DECIMAL(10, 2))
    cyclePathLeftHeight = Column(DECIMAL(10, 2))
    cyclePathRightWidth = Column(DECIMAL(10, 2))
    cyclePathRightHeight = Column(DECIMAL(10, 2))
    totalCyclePathWidth = Column(DECIMAL(10, 2))
    cyclePathMaterial = Column(String(100))
    
    # Pedestrian Path
    pedestrianPathPlacement = Column(String(50))
    pedestrianPathLeftWidth = Column(DECIMAL(10, 2))
    pedestrianPathLeftHeight = Column(DECIMAL(10, 2))
    pedestrianPathRightWidth = Column(DECIMAL(10, 2))
    pedestrianPathRightHeight = Column(DECIMAL(10, 2))
    totalPedestrianPathWidth = Column(DECIMAL(10, 2))
    totalPedestrianPathLength = Column(DECIMAL(15, 2))
    pedestrianPathMaterial = Column(String(100))
    
    # Infrastructure Count
    bridgeCount = Column(Integer)
    culvertCount = Column(Integer)
    
    # Status - IMPORTANT for routing
    status = Column(String(50), index=True)
    statusDescription = Column(Text)
    roadWork = Column(String(100))  # Type of road work
    
    # Municipality Info
    municipalityInfo = Column(Text)  # JSON
    
    # Visual
    color = Column(String(50))
    image = Column(String(500))
    
    # Metadata
    name = Column(String(255))
    alternateName = Column(String(255))
    description = Column(Text)
    areaServed = Column(String(255))
    address = Column(Text)  # JSON
    
    # Annotations
    annotations = Column(Text)  # JSON
    
    # Provenance
    dataProvider = Column(String(255))
    source = Column(String(255))
    owner = Column(Text)  # JSON
    seeAlso = Column(Text)  # JSON
    
    # Timestamps
    dateCreated = Column(DateTime, default=func.now())
    dateModified = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<RoadSegment(id={self.id}, name={self.roadName}, status={self.status})>"
