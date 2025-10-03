"""
CityWork Model
Construction and maintenance work zones for routing avoidance
"""

from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class CityWork(Base):
    __tablename__ = "CityWork"
    
    # Primary Key
    id = Column(String(255), primary_key=True)
    
    # Work Identification
    workNumber = Column(String(100), index=True)
    
    # Work Dates - IMPORTANT for routing
    startDate = Column(DateTime, index=True)
    endDate = Column(DateTime, index=True)
    workDate = Column(Text)
    workLastDateUpdate = Column(DateTime)
    dateLastReported = Column(DateTime)
    
    # Work Classification
    typeOfInterventionRequest = Column(String(100))
    workState = Column(String(100), index=True)  # 'planned', 'open', 'completed', etc.
    workNature = Column(Text)  # JSON
    workReason = Column(Text)  # JSON
    workTarget = Column(Text)  # JSON
    workLevel = Column(Text)  # JSON
    workZone = Column(Text)  # JSON
    workDisposition = Column(Text)  # JSON
    
    # Location - IMPORTANT for routing
    location = Column(Text)  # GeoJSON
    territorialArea = Column(String(255))
    
    # Impact Assessment
    isMainRoadImpactedHTR = Column(Boolean)
    isMobile = Column(Boolean)
    
    # Infrastructure Impact
    infrastructureFunction = Column(Text)  # JSON
    encroachment = Column(Text)  # JSON
    
    # Roads Impacted - IMPORTANT for routing
    roadImpacted = Column(Text)  # JSON
    roadImpactedMT = Column(Text)  # JSON
    roadImpactedSA = Column(Text)  # JSON
    countOfRoadImpacted = Column(Integer)
    
    # Public Transport Impact
    busImpacted = Column(Text)  # JSON
    countOfBusLineImpacted = Column(Integer)
    
    schoolBusImpacted = Column(Text)  # JSON
    countOfSchoolBusLineImpacted = Column(Integer)
    
    railwayImpacted = Column(Text)  # JSON
    countOfRailwayLineImpacted = Column(Integer)
    
    subwayImpacted = Column(Text)  # JSON
    countOfSubwayLineImpacted = Column(Integer)
    
    tramwayImpacted = Column(Text)  # JSON
    countOfTramwayLineImpacted = Column(Integer)
    
    stationImpacted = Column(Text)  # JSON
    countOfStationImpacted = Column(Integer)
    
    # Other Impact
    eventsImpacted = Column(Text)  # JSON
    countOfEventImpacted = Column(Integer)
    
    schoolImpacted = Column(Text)  # JSON
    countOfSchoolImpacted = Column(Integer)
    
    workOtherImpact = Column(Text)  # JSON
    
    # Vehicle Restrictions
    allowedVehicle = Column(Text)  # JSON
    maxAuthorizedTonnage = Column(Text)  # JSON
    
    # Contractors
    contractingAuthority = Column(String(255))
    mainContractingCompany = Column(String(255))
    othersContractingCompany = Column(Text)  # JSON
    
    # Derogation & Decrees
    countOfDerogation = Column(Integer)
    derogation = Column(Text)  # JSON
    decrees = Column(Text)  # JSON
    
    # Contact
    contactPoint = Column(Text)  # JSON
    
    # Opening Hours
    openingHoursSpecification = Column(Text)  # JSON
    
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
        return f"<CityWork(id={self.id}, state={self.workState}, number={self.workNumber})>"
