"""
Feature Engineering Service
Extracts and prepares features from database for ML prediction
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, List, Optional

from app.models.traffic import TrafficFlowObserved, RoadSegment


class FeatureEngineeringService:
    """
    Service to extract and engineer features from database
    for ML model prediction
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_segment_info(self, segment_id: str) -> Optional[Dict]:
        """Get road segment static information"""
        segment = self.db.query(RoadSegment).filter(
            RoadSegment.ID == segment_id
        ).first()
        
        if not segment:
            return None
        
        return {
            'segment_id': segment.ID,
            'name': segment.Name,
            'total_lanes': segment.TotalLaneNumber or 2,
            'max_speed': segment.MaximumAllowedSpeed or 40,
            'road_class': segment.RoadClass or 'Secondary'
        }
    
    def get_recent_traffic(
        self, 
        segment_id: str, 
        hours: int = 3,
        limit: int = 36  # 3 hours * 12 records/hour (5-min intervals)
    ) -> pd.DataFrame:
        """
        Get recent traffic data for feature engineering
        
        Args:
            segment_id: Road segment ID
            hours: Number of hours to look back
            limit: Maximum number of records
            
        Returns:
            DataFrame with recent traffic data
        """
        query = text("""
            SELECT TOP (:limit)
                t.ID,
                t.RefRoadSegment,
                t.DateObserved,
                t.DateObservedFrom,
                t.DateObservedTo,
                t.AverageVehicleSpeed,
                t.Intensity,
                t.Occupancy,
                t.Congested,
                r.Name as RoadName,
                r.TotalLaneNumber,
                r.MaximumAllowedSpeed,
                r.RoadClass
            FROM TrafficFlowObserved t
            JOIN RoadSegment r ON t.RefRoadSegment = r.ID
            WHERE t.RefRoadSegment = :segment_id
            AND t.DateObserved >= DATEADD(hour, -:hours, GETDATE())
            ORDER BY t.DateObserved DESC
        """)
        
        result = self.db.execute(
            query,
            {
                'segment_id': segment_id,
                'hours': hours,
                'limit': limit
            }
        )
        
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        
        if df.empty:
            return df
        
        # Sort by time ascending for feature engineering
        df = df.sort_values('DateObserved').reset_index(drop=True)
        
        return df
    
    def engineer_features(
        self,
        segment_id: str,
        target_datetime: Optional[datetime] = None
    ) -> Optional[Dict]:
        """
        Engineer all features required by ML models
        
        Args:
            segment_id: Road segment ID
            target_datetime: Time to predict for (default: now)
            
        Returns:
            Dictionary of features ready for model input
        """
        if target_datetime is None:
            target_datetime = datetime.now()
        
        # Get segment info
        segment_info = self.get_segment_info(segment_id)
        if not segment_info:
            return None
        
        # Get recent traffic data
        df = self.get_recent_traffic(segment_id, hours=3, limit=36)
        
        if df.empty or len(df) < 3:
            # Not enough data, return baseline features
            return self._get_baseline_features(segment_info, target_datetime)
        
        # Prepare base features
        features = {}
        
        # Static features
        features['TotalLaneNumber'] = segment_info['total_lanes']
        features['MaximumAllowedSpeed'] = segment_info['max_speed']
        
        # Temporal features
        features['hour'] = target_datetime.hour
        features['day_of_week'] = target_datetime.weekday()
        features['is_weekend'] = 1 if target_datetime.weekday() >= 5 else 0
        features['is_rush_hour'] = 1 if target_datetime.hour in [7, 8, 17, 18] else 0
        
        # Recent values (lags)
        recent_speed = df['AverageVehicleSpeed'].iloc[-3:].values
        recent_intensity = df['Intensity'].iloc[-3:].values
        
        features['speed_lag_1'] = recent_speed[-1] if len(recent_speed) >= 1 else segment_info['max_speed'] * 0.6
        features['speed_lag_2'] = recent_speed[-2] if len(recent_speed) >= 2 else segment_info['max_speed'] * 0.6
        features['speed_lag_3'] = recent_speed[-3] if len(recent_speed) >= 3 else segment_info['max_speed'] * 0.6
        
        features['intensity_lag_1'] = recent_intensity[-1] if len(recent_intensity) >= 1 else 5000
        
        # Rolling statistics
        if len(df) >= 6:
            features['speed_rolling_mean_6'] = df['AverageVehicleSpeed'].iloc[-6:].mean()
            features['speed_rolling_std_6'] = df['AverageVehicleSpeed'].iloc[-6:].std()
            features['intensity_rolling_mean_6'] = df['Intensity'].iloc[-6:].mean()
        else:
            features['speed_rolling_mean_6'] = features['speed_lag_1']
            features['speed_rolling_std_6'] = 2.0
            features['intensity_rolling_mean_6'] = features['intensity_lag_1']
        
        if len(df) >= 12:
            features['speed_rolling_mean_12'] = df['AverageVehicleSpeed'].iloc[-12:].mean()
        else:
            features['speed_rolling_mean_12'] = features['speed_lag_1']
        
        # Differences (trends)
        if len(df) >= 2:
            features['speed_diff'] = df['AverageVehicleSpeed'].iloc[-1] - df['AverageVehicleSpeed'].iloc[-2]
            features['intensity_diff'] = df['Intensity'].iloc[-1] - df['Intensity'].iloc[-2]
        else:
            features['speed_diff'] = 0.0
            features['intensity_diff'] = 0.0
        
        # Ratios
        features['speed_to_max_ratio'] = features['speed_lag_1'] / segment_info['max_speed']
        
        # Baseline speed (average for this hour and day of week)
        features['speed_baseline'] = self._get_baseline_speed(
            segment_id,
            target_datetime.hour,
            target_datetime.weekday()
        )
        
        # Current values (for recent prediction)
        latest = df.iloc[-1]
        features['Intensity'] = latest['Intensity']
        features['Occupancy'] = latest['Occupancy']
        
        # Segment encoding (one-hot for 10 segments)
        for i in range(1, 11):
            seg_id = f'segment_{i:03d}'
            features[f'segment_{seg_id}'] = 1 if segment_id == seg_id else 0
        
        return features
    
    def _get_baseline_speed(
        self,
        segment_id: str,
        hour: int,
        day_of_week: int
    ) -> float:
        """
        Calculate baseline speed for given hour and day of week
        """
        query = text("""
            SELECT AVG(AverageVehicleSpeed) as baseline_speed
            FROM TrafficFlowObserved
            WHERE RefRoadSegment = :segment_id
            AND DATEPART(HOUR, DateObserved) = :hour
            AND DATEPART(WEEKDAY, DateObserved) = :day_of_week
        """)
        
        result = self.db.execute(
            query,
            {
                'segment_id': segment_id,
                'hour': hour,
                'day_of_week': day_of_week + 1  # SQL weekday is 1-based
            }
        ).fetchone()
        
        if result and result[0]:
            return float(result[0])
        
        # Default baseline based on hour
        if hour in [7, 8, 17, 18]:
            return 15.0  # Rush hour
        elif hour >= 22 or hour <= 6:
            return 35.0  # Night
        else:
            return 25.0  # Normal
    
    def _get_baseline_features(
        self,
        segment_info: Dict,
        target_datetime: datetime
    ) -> Dict:
        """
        Generate baseline features when no historical data available
        """
        hour = target_datetime.hour
        is_rush_hour = 1 if hour in [7, 8, 17, 18] else 0
        
        # Estimate baseline values
        if is_rush_hour:
            base_speed = 15.0
            base_intensity = 8000.0
            base_occupancy = 0.75
        elif hour >= 22 or hour <= 6:
            base_speed = 35.0
            base_intensity = 3000.0
            base_occupancy = 0.30
        else:
            base_speed = 25.0
            base_intensity = 5500.0
            base_occupancy = 0.50
        
        features = {
            'TotalLaneNumber': segment_info['total_lanes'],
            'MaximumAllowedSpeed': segment_info['max_speed'],
            'hour': hour,
            'day_of_week': target_datetime.weekday(),
            'is_weekend': 1 if target_datetime.weekday() >= 5 else 0,
            'is_rush_hour': is_rush_hour,
            'speed_lag_1': base_speed,
            'speed_lag_2': base_speed,
            'speed_lag_3': base_speed,
            'intensity_lag_1': base_intensity,
            'speed_rolling_mean_6': base_speed,
            'speed_rolling_mean_12': base_speed,
            'speed_rolling_std_6': 2.0,
            'intensity_rolling_mean_6': base_intensity,
            'speed_diff': 0.0,
            'intensity_diff': 0.0,
            'speed_to_max_ratio': base_speed / segment_info['max_speed'],
            'speed_baseline': base_speed,
            'Intensity': base_intensity,
            'Occupancy': base_occupancy
        }
        
        # Segment encoding
        segment_id = segment_info['segment_id']
        for i in range(1, 11):
            seg_id = f'segment_{i:03d}'
            features[f'segment_{seg_id}'] = 1 if segment_id == seg_id else 0
        
        return features
    
    def get_current_traffic_status(self, segment_id: str) -> Optional[Dict]:
        """
        Get the most recent traffic observation for a segment
        """
        query = text("""
            SELECT TOP 1
                t.ID,
                t.RefRoadSegment,
                t.DateObserved,
                t.AverageVehicleSpeed,
                t.Intensity,
                t.Occupancy,
                t.Congested,
                r.Name as RoadName,
                r.RoadClass,
                r.TotalLaneNumber,
                r.MaximumAllowedSpeed
            FROM TrafficFlowObserved t
            JOIN RoadSegment r ON t.RefRoadSegment = r.ID
            WHERE t.RefRoadSegment = :segment_id
            ORDER BY t.DateObserved DESC
        """)
        
        result = self.db.execute(query, {'segment_id': segment_id}).fetchone()
        
        if not result:
            return None
        
        return {
            'segment_id': result.RefRoadSegment,
            'road_name': result.RoadName,
            'road_class': result.RoadClass,
            'timestamp': result.DateObserved,
            'speed': float(result.AverageVehicleSpeed),
            'intensity': float(result.Intensity),
            'occupancy': float(result.Occupancy),
            'congested': bool(result.Congested),
            'total_lanes': result.TotalLaneNumber,
            'max_speed': result.MaximumAllowedSpeed
        }
    
    def get_all_segments_current_status(self) -> List[Dict]:
        """
        Get current traffic status for all segments
        """
        query = text("""
            WITH LatestTraffic AS (
                SELECT 
                    RefRoadSegment,
                    MAX(DateObserved) as LatestTime
                FROM TrafficFlowObserved
                GROUP BY RefRoadSegment
            )
            SELECT 
                t.RefRoadSegment,
                r.Name as RoadName,
                t.DateObserved,
                t.AverageVehicleSpeed,
                t.Intensity,
                t.Occupancy,
                t.Congested,
                r.RoadClass
            FROM TrafficFlowObserved t
            JOIN LatestTraffic lt ON t.RefRoadSegment = lt.RefRoadSegment 
                AND t.DateObserved = lt.LatestTime
            JOIN RoadSegment r ON t.RefRoadSegment = r.ID
            ORDER BY t.RefRoadSegment
        """)
        
        results = self.db.execute(query).fetchall()
        
        return [
            {
                'segment_id': row.RefRoadSegment,
                'road_name': row.RoadName,
                'road_class': row.RoadClass,
                'timestamp': row.DateObserved,
                'speed': float(row.AverageVehicleSpeed),
                'intensity': float(row.Intensity),
                'occupancy': float(row.Occupancy),
                'congested': bool(row.Congested)
            }
            for row in results
        ]
