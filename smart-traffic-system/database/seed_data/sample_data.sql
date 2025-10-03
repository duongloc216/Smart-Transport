/*
===================================================================================
SAMPLE DATA FOR SMART TRAFFIC SYSTEM
===================================================================================
This script inserts sample data for testing and development
Location: Ho Chi Minh City, Vietnam (Districts 1 & 3)
===================================================================================
*/

USE SmartTrafficDB;
GO

PRINT 'Inserting sample data...';
GO

-- ===================================================================================
-- 1. SAMPLE ROADS
-- ===================================================================================

INSERT INTO Road (id, name, roadClass, length, location, description) VALUES
('road_001', 'Nguyen Hue Boulevard', 'primary', 1500.00, 
 '{"type":"LineString","coordinates":[[106.70249,10.77436],[106.70380,10.77536],[106.70511,10.77636]]}',
 'Main boulevard in District 1'),
 
('road_002', 'Le Loi Street', 'primary', 2000.00,
 '{"type":"LineString","coordinates":[[106.69893,10.77289],[106.70249,10.77436],[106.70605,10.77583]]}',
 'Major street connecting District 1'),
 
('road_003', 'Dong Khoi Street', 'secondary', 1200.00,
 '{"type":"LineString","coordinates":[[106.70380,10.77136],[106.70380,10.77536],[106.70380,10.77936]]}',
 'Historic shopping street');
GO

-- ===================================================================================
-- 2. SAMPLE ROAD SEGMENTS
-- ===================================================================================

INSERT INTO RoadSegment (
    id, roadId, roadName, roadClass, maximumAllowedSpeed, minimumAllowedSpeed,
    totalLaneNumber, length, location, status
) VALUES
-- Nguyen Hue segments
('segment_001', 'road_001', 'Nguyen Hue - Segment 1', 'MAJOR_CITY_ROAD', 
 40.00, 10.00, 4, 500.00,
 '{"type":"LineString","coordinates":[[106.70249,10.77436],[106.70380,10.77536]]}', 'open'),
 
('segment_002', 'road_001', 'Nguyen Hue - Segment 2', 'MAJOR_CITY_ROAD',
 40.00, 10.00, 4, 500.00,
 '{"type":"LineString","coordinates":[[106.70380,10.77536],[106.70511,10.77636]]}', 'open'),

-- Le Loi segments  
('segment_003', 'road_002', 'Le Loi - Segment 1', 'MAJOR_CITY_ROAD',
 50.00, 20.00, 6, 800.00,
 '{"type":"LineString","coordinates":[[106.69893,10.77289],[106.70249,10.77436]]}', 'open'),
 
('segment_004', 'road_002', 'Le Loi - Segment 2', 'MAJOR_CITY_ROAD',
 50.00, 20.00, 6, 800.00,
 '{"type":"LineString","coordinates":[[106.70249,10.77436],[106.70605,10.77583]]}', 'open'),

-- Dong Khoi segments
('segment_005', 'road_003', 'Dong Khoi - Segment 1', 'MINOR_CITY_ROAD',
 30.00, 10.00, 2, 400.00,
 '{"type":"LineString","coordinates":[[106.70380,10.77136],[106.70380,10.77536]]}', 'open'),
 
('segment_006', 'road_003', 'Dong Khoi - Segment 2', 'MINOR_CITY_ROAD',
 30.00, 10.00, 2, 400.00,
 '{"type":"LineString","coordinates":[[106.70380,10.77536],[106.70380,10.77936]]}', 'open');
GO

-- ===================================================================================
-- 3. SAMPLE TRAFFIC FLOW DATA (Last 24 hours)
-- ===================================================================================

DECLARE @i INT = 0;
DECLARE @datetime DATETIME2;
DECLARE @segment NVARCHAR(255);
DECLARE @speed DECIMAL(10,2);
DECLARE @intensity INT;
DECLARE @occupancy DECIMAL(5,4);

WHILE @i < 288 DO -- 288 = 24 hours * 12 (every 5 minutes)
BEGIN
    SET @datetime = DATEADD(MINUTE, -(@i * 5), GETDATE());
    
    -- Traffic pattern: rush hour simulation
    DECLARE @hour INT = DATEPART(HOUR, @datetime);
    DECLARE @traffic_factor DECIMAL(5,2);
    
    -- Morning rush (7-9 AM) and evening rush (5-7 PM)
    IF (@hour >= 7 AND @hour <= 9) OR (@hour >= 17 AND @hour <= 19)
        SET @traffic_factor = 1.5;
    ELSE IF (@hour >= 22 OR @hour <= 5)
        SET @traffic_factor = 0.3;
    ELSE
        SET @traffic_factor = 1.0;
    
    -- Insert for segment_001
    INSERT INTO TrafficFlowObserved (
        id, refRoadSegment, dateObservedFrom, dateObservedTo,
        averageVehicleSpeed, intensity, occupancy, congested,
        laneDirection, vehicleType
    ) VALUES (
        'traffic_seg1_' + CONVERT(VARCHAR(50), @i),
        'segment_001',
        @datetime,
        DATEADD(MINUTE, 5, @datetime),
        40.0 / @traffic_factor,
        CAST(100 * @traffic_factor AS INT),
        CASE WHEN @traffic_factor > 1.3 THEN 0.75 ELSE 0.45 END,
        CASE WHEN @traffic_factor > 1.3 THEN 1 ELSE 0 END,
        'forward',
        'car'
    );
    
    -- Insert for segment_003 (major road - more traffic)
    INSERT INTO TrafficFlowObserved (
        id, refRoadSegment, dateObservedFrom, dateObservedTo,
        averageVehicleSpeed, intensity, occupancy, congested,
        laneDirection, vehicleType
    ) VALUES (
        'traffic_seg3_' + CONVERT(VARCHAR(50), @i),
        'segment_003',
        @datetime,
        DATEADD(MINUTE, 5, @datetime),
        48.0 / @traffic_factor,
        CAST(180 * @traffic_factor AS INT),
        CASE WHEN @traffic_factor > 1.3 THEN 0.82 ELSE 0.55 END,
        CASE WHEN @traffic_factor > 1.3 THEN 1 ELSE 0 END,
        'forward',
        'car'
    );
    
    SET @i = @i + 1;
END;
GO

PRINT 'Inserted ' + CAST(@@ROWCOUNT AS VARCHAR) + ' traffic flow records';
GO

-- ===================================================================================
-- 4. SAMPLE VEHICLES
-- ===================================================================================

INSERT INTO Vehicle (
    id, vehiclePlateIdentifier, vehicleType, location, speed,
    serviceStatus, vehicleRunningStatus, observationDateTime
) VALUES
('vehicle_001', '59A-12345', 'car', 
 '{"type":"Point","coordinates":[106.70300,10.77500]}',
 '{"value":35,"unitCode":"KMH"}',
 'onRoute', 'running', GETDATE()),

('vehicle_002', '59B-67890', 'bus',
 '{"type":"Point","coordinates":[106.70100,10.77350]}',
 '{"value":28,"unitCode":"KMH"}',
 'onRoute', 'running', GETDATE()),

('vehicle_003', '59C-11111', 'motorcycle',
 '{"type":"Point","coordinates":[106.70400,10.77600]}',
 '{"value":42,"unitCode":"KMH"}',
 'onRoute', 'running', GETDATE()),

('vehicle_004', '59D-22222', 'truck',
 '{"type":"Point","coordinates":[106.70000,10.77300]}',
 '{"value":25,"unitCode":"KMH"}',
 'onRoute', 'running', GETDATE()),

('vehicle_005', '59E-33333', 'car',
 '{"type":"Point","coordinates":[106.70500,10.77700]}',
 '{"value":0,"unitCode":"KMH"}',
 'parked', 'stopped', GETDATE());
GO

PRINT 'Inserted 5 sample vehicles';
GO

-- ===================================================================================
-- 5. SAMPLE ROAD ACCIDENTS
-- ===================================================================================

INSERT INTO RoadAccident (
    id, localId, accidentDate, location, roadClass, status,
    accidentType, severity, numPassengersInjured, totalInjured,
    description, vehiclesInvolved
) VALUES
-- Active accident (just happened)
('accident_001', 'ACC-2025-001', DATEADD(MINUTE, -30, GETDATE()),
 '{"type":"Point","coordinates":[106.70250,10.77450]}',
 'primary', 'onGoing',
 '["collision"]', 'medium', 2, 2,
 'Minor collision between two cars on Nguyen Hue Boulevard',
 '["car","car"]'),

-- Solved accident (2 hours ago)
('accident_002', 'ACC-2025-002', DATEADD(HOUR, -2, GETDATE()),
 '{"type":"Point","coordinates":[106.70100,10.77300]}',
 'primary', 'solved',
 '["collision"]', 'low', 1, 1,
 'Motorcycle accident on Le Loi Street',
 '["motorcycle"]');
GO

PRINT 'Inserted 2 sample accidents';
GO

-- ===================================================================================
-- 6. SAMPLE CITY WORKS (Construction)
-- ===================================================================================

INSERT INTO CityWork (
    id, workNumber, startDate, endDate, workState, location,
    name, description, workNature, countOfRoadImpacted,
    mainContractingCompany
) VALUES
-- Active construction
('work_001', 'WORK-2025-001', 
 DATEADD(DAY, -5, GETDATE()), 
 DATEADD(DAY, 25, GETDATE()),
 'open',
 '{"type":"Polygon","coordinates":[[[106.70380,10.77400],[106.70430,10.77400],[106.70430,10.77450],[106.70380,10.77450],[106.70380,10.77400]]]}',
 'Road Maintenance - Nguyen Hue',
 'Resurfacing and lane marking renovation',
 '["maintenance","resurfacing"]',
 1,
 'HCMC Public Works Company'),

-- Planned construction
('work_002', 'WORK-2025-002',
 DATEADD(DAY, 10, GETDATE()),
 DATEADD(DAY, 40, GETDATE()),
 'planned',
 '{"type":"Polygon","coordinates":[[[106.70000,10.77200],[106.70100,10.77200],[106.70100,10.77300],[106.70000,10.77300],[106.70000,10.77200]]]}',
 'Drainage System Upgrade - Le Loi',
 'Underground drainage pipe replacement',
 '["construction","drainage"]',
 1,
 'Infrastructure Development Corp');
GO

PRINT 'Inserted 2 sample construction zones';
GO

-- ===================================================================================
-- VERIFY DATA
-- ===================================================================================

PRINT '';
PRINT '===================================================================================';
PRINT 'DATA VERIFICATION';
PRINT '===================================================================================';

SELECT 'Roads' AS TableName, COUNT(*) AS RecordCount FROM Road
UNION ALL
SELECT 'RoadSegments', COUNT(*) FROM RoadSegment
UNION ALL
SELECT 'TrafficFlowObserved', COUNT(*) FROM TrafficFlowObserved
UNION ALL
SELECT 'Vehicles', COUNT(*) FROM Vehicle
UNION ALL
SELECT 'RoadAccidents', COUNT(*) FROM RoadAccident
UNION ALL
SELECT 'CityWorks', COUNT(*) FROM CityWork;

PRINT '';
PRINT 'Sample data inserted successfully!';
PRINT '';

-- Show current traffic conditions
PRINT 'Current Traffic Conditions:';
SELECT TOP 5 
    refRoadSegment,
    dateObservedFrom,
    averageVehicleSpeed,
    intensity,
    occupancy,
    CASE WHEN congested = 1 THEN 'Yes' ELSE 'No' END AS Congested
FROM TrafficFlowObserved
ORDER BY dateObservedFrom DESC;

GO
