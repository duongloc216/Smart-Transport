/*
===================================================================================
SMART TRAFFIC SYSTEM - DATABASE SCHEMA FOR SQL SERVER
===================================================================================
Created: 2025-10-03
Database: SmartTrafficDB
Purpose: AI-Powered Traffic Prediction & Smart Routing System

Data Models:
1. TrafficFlowObserved - Real-time traffic flow data
2. Vehicle - Vehicle tracking and information
3. Road - Road network structure
4. RoadSegment - Detailed road segments with lanes and capacity
5. RoadAccident - Traffic accident records
6. CityWork - Construction and maintenance work zones

===================================================================================
*/

-- Create Database
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'SmartTrafficDB')
BEGIN
    CREATE DATABASE SmartTrafficDB;
END
GO

USE SmartTrafficDB;
GO

-- ===================================================================================
-- 1. TRAFFIC FLOW OBSERVED TABLE
-- ===================================================================================
CREATE TABLE TrafficFlowObserved (
    -- Primary Key
    id NVARCHAR(255) PRIMARY KEY,
    
    -- Observed Data
    dateObserved NVARCHAR(100),
    dateObservedFrom DATETIME2,
    dateObservedTo DATETIME2,
    
    -- Traffic Metrics
    intensity DECIMAL(18,2),              -- Number of vehicles
    averageVehicleSpeed DECIMAL(10,2),    -- km/h
    occupancy DECIMAL(5,4),                -- 0-1 ratio
    averageGapDistance DECIMAL(10,2),     -- meters
    averageHeadwayTime DECIMAL(10,2),     -- seconds
    averageVehicleLength DECIMAL(10,2),   -- meters
    
    -- Lane Information
    laneId INT,
    laneDirection NVARCHAR(20),           -- 'forward', 'backward'
    reversedLane BIT,
    
    -- Vehicle Type
    vehicleType NVARCHAR(50),             -- 'car', 'bus', 'truck', etc.
    vehicleSubType NVARCHAR(100),
    
    -- Status
    congested BIT,
    
    -- References
    refRoadSegment NVARCHAR(255),         -- FK to RoadSegment
    
    -- Location (GeoJSON stored as JSON)
    location NVARCHAR(MAX),               -- GeoJSON Point
    address NVARCHAR(MAX),                -- JSON
    
    -- Metadata
    name NVARCHAR(255),
    alternateName NVARCHAR(255),
    description NVARCHAR(MAX),
    areaServed NVARCHAR(255),
    
    -- Provenance
    dataProvider NVARCHAR(255),
    source NVARCHAR(255),
    owner NVARCHAR(MAX),                  -- JSON
    seeAlso NVARCHAR(MAX),                -- JSON
    
    -- Timestamps
    dateCreated DATETIME2 DEFAULT GETDATE(),
    dateModified DATETIME2 DEFAULT GETDATE(),
    
    -- Indexes
    INDEX IX_TrafficFlow_RoadSegment (refRoadSegment),
    INDEX IX_TrafficFlow_DateObserved (dateObservedFrom, dateObservedTo),
    INDEX IX_TrafficFlow_Created (dateCreated)
);
GO

-- ===================================================================================
-- 2. VEHICLE TABLE
-- ===================================================================================
CREATE TABLE Vehicle (
    -- Primary Key
    id NVARCHAR(255) PRIMARY KEY,
    
    -- Vehicle Identification
    vehiclePlateIdentifier NVARCHAR(50),
    vehicleIdentificationNumber NVARCHAR(100),
    license_plate NVARCHAR(50),
    fleetVehicleId NVARCHAR(100),
    
    -- Vehicle Type & Configuration
    vehicleType NVARCHAR(100),            -- 'car', 'bus', 'truck', 'motorcycle', etc.
    vehicleConfiguration NVARCHAR(100),
    vehicleSpecialUsage NVARCHAR(50),     -- 'ambulance', 'police', 'taxi', etc.
    emergencyVehicleType NVARCHAR(50),
    
    -- Category & Classification
    category NVARCHAR(MAX),               -- JSON array
    
    -- Physical Attributes
    color NVARCHAR(50),
    cargoWeight DECIMAL(10,2),
    
    -- Location & Movement
    location NVARCHAR(MAX),               -- GeoJSON Point
    previousLocation NVARCHAR(MAX),       -- GeoJSON Point
    bearing DECIMAL(10,2),                -- degrees
    heading NVARCHAR(MAX),                -- JSON
    speed NVARCHAR(MAX),                  -- JSON with value and unit
    vehicleAltitude NVARCHAR(100),
    
    -- Status
    serviceStatus NVARCHAR(50),           -- 'parked', 'onRoute', 'broken', 'outOfService'
    vehicleRunningStatus NVARCHAR(50),    -- 'running', 'stopped', 'waiting'
    serviceOnDuty BIT,
    ignitionStatus BIT,
    
    -- Battery & Device
    battery DECIMAL(5,2),                 -- percentage
    deviceBatteryStatus NVARCHAR(50),     -- 'connected', 'disconnected'
    deviceSimNumber NVARCHAR(50),
    vehicleTrackerDevice NVARCHAR(255),
    
    -- Fuel
    fuelType NVARCHAR(50),
    fuelFilled DECIMAL(10,2),
    fuelEfficiency DECIMAL(10,2),
    
    -- Mileage & Trip
    mileageFromOdometer DECIMAL(15,2),
    currentTripCount INT,
    tripNetWeightCollected DECIMAL(10,2),
    
    -- Service Information
    serviceProvided NVARCHAR(MAX),        -- JSON
    
    -- Dates
    dateFirstUsed DATE,
    dateVehicleFirstRegistered DATE,
    purchaseDate DATETIME2,
    observationDateTime DATETIME2,
    
    -- Municipality Info
    municipalityInfo NVARCHAR(MAX),       -- JSON
    wardId NVARCHAR(50),
    wardName NVARCHAR(255),
    zoneName NVARCHAR(255),
    
    -- Metadata
    name NVARCHAR(255),
    alternateName NVARCHAR(255),
    description NVARCHAR(MAX),
    areaServed NVARCHAR(255),
    address NVARCHAR(MAX),                -- JSON
    
    -- Media
    image NVARCHAR(500),
    
    -- Annotations & Features
    annotations NVARCHAR(MAX),            -- JSON
    feature NVARCHAR(MAX),                -- JSON
    
    -- Report
    reportId NVARCHAR(100),
    
    -- Provenance
    dataProvider NVARCHAR(255),
    source NVARCHAR(255),
    owner NVARCHAR(MAX),                  -- JSON
    seeAlso NVARCHAR(MAX),                -- JSON
    
    -- Timestamps
    dateCreated DATETIME2 DEFAULT GETDATE(),
    dateModified DATETIME2 DEFAULT GETDATE(),
    
    -- Indexes
    INDEX IX_Vehicle_Plate (vehiclePlateIdentifier),
    INDEX IX_Vehicle_Type (vehicleType),
    INDEX IX_Vehicle_Status (serviceStatus),
    INDEX IX_Vehicle_ObservationDate (observationDateTime)
);
GO

-- ===================================================================================
-- 3. ROAD TABLE
-- ===================================================================================
CREATE TABLE Road (
    -- Primary Key
    id NVARCHAR(255) PRIMARY KEY,
    
    -- Road Classification
    roadClass NVARCHAR(50),               -- 'motorway', 'primary', 'secondary', etc.
    
    -- Physical Attributes
    length DECIMAL(15,2),                 -- meters
    
    -- Location (GeoJSON LineString)
    location NVARCHAR(MAX),               -- GeoJSON LineString
    
    -- Road Segments Reference
    refRoadSegment NVARCHAR(MAX),         -- JSON array of segment IDs
    
    -- Responsibility
    responsible NVARCHAR(255),
    
    -- Visual
    color NVARCHAR(50),
    image NVARCHAR(500),
    
    -- Metadata
    name NVARCHAR(255),
    alternateName NVARCHAR(255),
    description NVARCHAR(MAX),
    areaServed NVARCHAR(255),
    address NVARCHAR(MAX),                -- JSON
    
    -- Annotations
    annotations NVARCHAR(MAX),            -- JSON
    
    -- Provenance
    dataProvider NVARCHAR(255),
    source NVARCHAR(255),
    owner NVARCHAR(MAX),                  -- JSON
    seeAlso NVARCHAR(MAX),                -- JSON
    
    -- Timestamps
    dateCreated DATETIME2 DEFAULT GETDATE(),
    dateModified DATETIME2 DEFAULT GETDATE(),
    
    -- Indexes
    INDEX IX_Road_Class (roadClass),
    INDEX IX_Road_Name (name)
);
GO

-- ===================================================================================
-- 4. ROAD SEGMENT TABLE
-- ===================================================================================
CREATE TABLE RoadSegment (
    -- Primary Key
    id NVARCHAR(255) PRIMARY KEY,
    
    -- Segment Identification
    roadId NVARCHAR(255),
    roadName NVARCHAR(255),
    agency_name NVARCHAR(255),
    
    -- Classification
    roadClass NVARCHAR(100),              -- Highway classification
    category NVARCHAR(MAX),               -- JSON array
    
    -- Location
    location NVARCHAR(MAX),               -- GeoJSON LineString
    startPoint NVARCHAR(MAX),             -- GeoJSON Point
    endPoint NVARCHAR(MAX),               -- GeoJSON Point
    
    -- Kilometer Posts
    startKilometer DECIMAL(10,3),
    endKilometer DECIMAL(10,3),
    
    -- Physical Dimensions
    length DECIMAL(15,2),                 -- meters
    width DECIMAL(10,2),                  -- meters
    carriagewayLength DECIMAL(15,2),
    carriagewayWidth DECIMAL(10,2),
    rightOfWayWidth DECIMAL(10,2),
    
    -- Lane Information
    totalLaneNumber INT,
    laneInfo NVARCHAR(MAX),               -- JSON
    laneUsage NVARCHAR(MAX),              -- JSON
    
    -- Speed Limits
    maximumAllowedSpeed DECIMAL(10,2),    -- km/h
    minimumAllowedSpeed DECIMAL(10,2),    -- km/h
    
    -- Weight & Size Restrictions
    maximumAllowedHeight DECIMAL(10,2),   -- meters
    maximumAllowedWeight DECIMAL(10,2),   -- tons
    maximumAllowedWidth DECIMAL(10,2),    -- meters
    
    -- Allowed Vehicles
    allowedVehicleType NVARCHAR(MAX),     -- JSON
    
    -- Road Material
    roadMaterial NVARCHAR(100),
    
    -- Road Direction
    roadDirection NVARCHAR(50),
    
    -- Median
    medianLength DECIMAL(15,2),
    medianWidth DECIMAL(10,2),
    medianHeight DECIMAL(10,2),
    
    -- Cycle Path
    cyclePathPlacement NVARCHAR(50),      -- 'LEFT', 'RIGHT', 'BOTH', 'NOT_AVAILABLE'
    cyclePathLeftWidth DECIMAL(10,2),
    cyclePathLeftHeight DECIMAL(10,2),
    cyclePathRightWidth DECIMAL(10,2),
    cyclePathRightHeight DECIMAL(10,2),
    totalCyclePathWidth DECIMAL(10,2),
    cyclePathMaterial NVARCHAR(100),
    
    -- Pedestrian Path
    pedestrianPathPlacement NVARCHAR(50),
    pedestrianPathLeftWidth DECIMAL(10,2),
    pedestrianPathLeftHeight DECIMAL(10,2),
    pedestrianPathRightWidth DECIMAL(10,2),
    pedestrianPathRightHeight DECIMAL(10,2),
    totalPedestrianPathWidth DECIMAL(10,2),
    totalPedestrianPathLength DECIMAL(15,2),
    pedestrianPathMaterial NVARCHAR(100),
    
    -- Infrastructure Count
    bridgeCount INT,
    culvertCount INT,
    
    -- Status
    status NVARCHAR(50),
    statusDescription NVARCHAR(MAX),
    roadWork NVARCHAR(100),               -- Type of road work
    
    -- Municipality Info
    municipalityInfo NVARCHAR(MAX),       -- JSON
    
    -- Visual
    color NVARCHAR(50),
    image NVARCHAR(500),
    
    -- Metadata
    name NVARCHAR(255),
    alternateName NVARCHAR(255),
    description NVARCHAR(MAX),
    areaServed NVARCHAR(255),
    address NVARCHAR(MAX),                -- JSON
    
    -- Annotations
    annotations NVARCHAR(MAX),            -- JSON
    
    -- Provenance
    dataProvider NVARCHAR(255),
    source NVARCHAR(255),
    owner NVARCHAR(MAX),                  -- JSON
    seeAlso NVARCHAR(MAX),                -- JSON
    
    -- Timestamps
    dateCreated DATETIME2 DEFAULT GETDATE(),
    dateModified DATETIME2 DEFAULT GETDATE(),
    
    -- Indexes
    INDEX IX_RoadSegment_RoadId (roadId),
    INDEX IX_RoadSegment_Class (roadClass),
    INDEX IX_RoadSegment_Status (status),
    INDEX IX_RoadSegment_Name (roadName)
);
GO

-- ===================================================================================
-- 5. ROAD ACCIDENT TABLE
-- ===================================================================================
CREATE TABLE RoadAccident (
    -- Primary Key
    id NVARCHAR(255) PRIMARY KEY,
    localId NVARCHAR(100),
    
    -- Accident Date & Time
    accidentDate DATETIME2,
    accidentStatisticalDate NVARCHAR(MAX), -- JSON
    
    -- Accident Details
    accidentType NVARCHAR(MAX),            -- JSON
    accidentDescription NVARCHAR(MAX),     -- JSON
    accidentLocation NVARCHAR(50),         -- Enum value
    
    -- Location
    location NVARCHAR(MAX),                -- GeoJSON Point
    
    -- Road Information
    roadClass NVARCHAR(100),
    roadIntersection NVARCHAR(50),
    roadPaving NVARCHAR(50),
    roadSign NVARCHAR(50),
    roadSurface NVARCHAR(50),
    roadTrunk NVARCHAR(50),
    
    -- Casualties
    numPassengersDead INT DEFAULT 0,
    numPassengersInjured INT DEFAULT 0,
    numPedestrianDead INT DEFAULT 0,
    numPedestrianInjured INT DEFAULT 0,
    totalDeadPeopleWithin24Hours INT DEFAULT 0,
    totalDeadPeopleWithin30Days INT DEFAULT 0,
    totalInjured INT DEFAULT 0,
    
    -- Involved Parties
    pedestriansInvolved BIT,
    vehiclesInvolved NVARCHAR(MAX),        -- JSON
    weakestSubject NVARCHAR(50),
    
    -- Weather Conditions
    weatherConditions NVARCHAR(MAX),       -- JSON
    
    -- Status
    status NVARCHAR(50),                   -- 'onGoing', 'solved', 'archived'
    
    -- Metadata
    name NVARCHAR(255),
    alternateName NVARCHAR(255),
    description NVARCHAR(MAX),
    areaServed NVARCHAR(255),
    address NVARCHAR(MAX),                 -- JSON
    
    -- Provenance
    dataProvider NVARCHAR(255),
    source NVARCHAR(255),
    owner NVARCHAR(MAX),                   -- JSON
    seeAlso NVARCHAR(MAX),                 -- JSON
    
    -- Timestamps
    dateCreated DATETIME2 DEFAULT GETDATE(),
    dateModified DATETIME2 DEFAULT GETDATE(),
    
    -- Indexes
    INDEX IX_Accident_Date (accidentDate),
    INDEX IX_Accident_Status (status),
    INDEX IX_Accident_Location (roadClass)
);
GO

-- ===================================================================================
-- 6. CITY WORK TABLE (Construction & Maintenance)
-- ===================================================================================
CREATE TABLE CityWork (
    -- Primary Key
    id NVARCHAR(255) PRIMARY KEY,
    
    -- Work Identification
    workNumber NVARCHAR(100),
    
    -- Work Dates
    startDate DATETIME2,
    endDate DATETIME2,
    workDate NVARCHAR(MAX),
    workLastDateUpdate DATETIME2,
    dateLastReported DATETIME2,
    
    -- Work Classification
    typeOfInterventionRequest NVARCHAR(100), -- 'urgentWorks', 'authorizationRequest', etc.
    workState NVARCHAR(100),                  -- 'planned', 'open', 'completed', etc.
    workNature NVARCHAR(MAX),                 -- JSON
    workReason NVARCHAR(MAX),                 -- JSON
    workTarget NVARCHAR(MAX),                 -- JSON
    workLevel NVARCHAR(MAX),                  -- JSON
    workZone NVARCHAR(MAX),                   -- JSON
    workDisposition NVARCHAR(MAX),            -- JSON
    
    -- Location
    location NVARCHAR(MAX),                   -- GeoJSON
    territorialArea NVARCHAR(255),
    
    -- Impact Assessment
    isMainRoadImpactedHTR BIT,
    isMobile BIT,
    
    -- Infrastructure Impact
    infrastructureFunction NVARCHAR(MAX),     -- JSON
    encroachment NVARCHAR(MAX),               -- JSON
    
    -- Roads Impacted
    roadImpacted NVARCHAR(MAX),               -- JSON
    roadImpactedMT NVARCHAR(MAX),             -- JSON
    roadImpactedSA NVARCHAR(MAX),             -- JSON
    countOfRoadImpacted INT,
    
    -- Public Transport Impact
    busImpacted NVARCHAR(MAX),                -- JSON
    countOfBusLineImpacted INT,
    
    schoolBusImpacted NVARCHAR(MAX),          -- JSON
    countOfSchoolBusLineImpacted INT,
    
    railwayImpacted NVARCHAR(MAX),            -- JSON
    countOfRailwayLineImpacted INT,
    
    subwayImpacted NVARCHAR(MAX),             -- JSON
    countOfSubwayLineImpacted INT,
    
    tramwayImpacted NVARCHAR(MAX),            -- JSON
    countOfTramwayLineImpacted INT,
    
    stationImpacted NVARCHAR(MAX),            -- JSON
    countOfStationImpacted INT,
    
    -- Other Impact
    eventsImpacted NVARCHAR(MAX),             -- JSON
    countOfEventImpacted INT,
    
    schoolImpacted NVARCHAR(MAX),             -- JSON
    countOfSchoolImpacted INT,
    
    workOtherImpact NVARCHAR(MAX),            -- JSON
    
    -- Vehicle Restrictions
    allowedVehicle NVARCHAR(MAX),             -- JSON
    maxAuthorizedTonnage NVARCHAR(MAX),       -- JSON
    
    -- Contractors
    contractingAuthority NVARCHAR(255),
    mainContractingCompany NVARCHAR(255),
    othersContractingCompany NVARCHAR(MAX),   -- JSON
    
    -- Derogation & Decrees
    countOfDerogation INT,
    derogation NVARCHAR(MAX),                 -- JSON
    decrees NVARCHAR(MAX),                    -- JSON
    
    -- Contact
    contactPoint NVARCHAR(MAX),               -- JSON
    
    -- Opening Hours
    openingHoursSpecification NVARCHAR(MAX),  -- JSON
    
    -- Metadata
    name NVARCHAR(255),
    alternateName NVARCHAR(255),
    description NVARCHAR(MAX),
    areaServed NVARCHAR(255),
    address NVARCHAR(MAX),                    -- JSON
    
    -- Provenance
    dataProvider NVARCHAR(255),
    source NVARCHAR(255),
    owner NVARCHAR(MAX),                      -- JSON
    seeAlso NVARCHAR(MAX),                    -- JSON
    
    -- Timestamps
    dateCreated DATETIME2 DEFAULT GETDATE(),
    dateModified DATETIME2 DEFAULT GETDATE(),
    
    -- Indexes
    INDEX IX_CityWork_State (workState),
    INDEX IX_CityWork_Dates (startDate, endDate),
    INDEX IX_CityWork_Number (workNumber)
);
GO

-- ===================================================================================
-- FOREIGN KEY CONSTRAINTS
-- ===================================================================================

-- TrafficFlowObserved -> RoadSegment
ALTER TABLE TrafficFlowObserved
ADD CONSTRAINT FK_TrafficFlow_RoadSegment
FOREIGN KEY (refRoadSegment) REFERENCES RoadSegment(id);
GO

-- ===================================================================================
-- VIEWS FOR COMMON QUERIES
-- ===================================================================================

-- View: Current Traffic Conditions
CREATE VIEW vw_CurrentTrafficConditions AS
SELECT 
    t.id,
    t.refRoadSegment,
    rs.roadName,
    rs.roadClass,
    t.dateObservedFrom,
    t.averageVehicleSpeed,
    t.intensity,
    t.occupancy,
    t.congested,
    CASE 
        WHEN t.occupancy >= 0.8 THEN 'Heavy'
        WHEN t.occupancy >= 0.5 THEN 'Moderate'
        ELSE 'Light'
    END AS trafficLevel
FROM TrafficFlowObserved t
LEFT JOIN RoadSegment rs ON t.refRoadSegment = rs.id
WHERE t.dateObservedFrom >= DATEADD(HOUR, -1, GETDATE());
GO

-- View: Active Accidents
CREATE VIEW vw_ActiveAccidents AS
SELECT 
    id,
    localId,
    accidentDate,
    location,
    roadClass,
    status,
    totalInjured,
    totalDeadPeopleWithin24Hours,
    DATEDIFF(MINUTE, accidentDate, GETDATE()) AS minutesSinceAccident
FROM RoadAccident
WHERE status = 'onGoing';
GO

-- View: Active Construction Zones
CREATE VIEW vw_ActiveConstructionZones AS
SELECT 
    id,
    workNumber,
    startDate,
    endDate,
    workState,
    location,
    countOfRoadImpacted,
    mainContractingCompany,
    DATEDIFF(DAY, GETDATE(), endDate) AS daysUntilCompletion
FROM CityWork
WHERE workState IN ('open', 'planned')
    AND startDate <= GETDATE()
    AND (endDate IS NULL OR endDate >= GETDATE());
GO

-- ===================================================================================
-- STORED PROCEDURES
-- ===================================================================================

-- Procedure: Get Road Status
CREATE PROCEDURE sp_GetRoadStatus
    @roadSegmentId NVARCHAR(255)
AS
BEGIN
    SELECT 
        rs.id,
        rs.roadName,
        rs.roadClass,
        rs.status,
        rs.maximumAllowedSpeed,
        
        -- Latest Traffic
        t.averageVehicleSpeed AS currentSpeed,
        t.occupancy,
        t.congested,
        
        -- Active Accidents
        (SELECT COUNT(*) FROM RoadAccident 
         WHERE roadClass = rs.roadClass 
         AND status = 'onGoing') AS activeAccidents,
        
        -- Active Construction
        (SELECT COUNT(*) FROM CityWork 
         WHERE workState = 'open'
         AND JSON_VALUE(roadImpacted, '$[0]') = @roadSegmentId) AS activeConstruction
         
    FROM RoadSegment rs
    LEFT JOIN (
        SELECT TOP 1 * 
        FROM TrafficFlowObserved 
        WHERE refRoadSegment = @roadSegmentId 
        ORDER BY dateObservedFrom DESC
    ) t ON 1=1
    WHERE rs.id = @roadSegmentId;
END;
GO

PRINT 'Database schema created successfully!';
PRINT 'Total tables: 6';
PRINT 'Total views: 3';
PRINT 'Total stored procedures: 1';
GO
