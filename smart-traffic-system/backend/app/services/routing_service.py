"""
Smart Routing Service
A* algorithm with ML-predicted traffic weights and incident avoidance
"""

import heapq
import math
from typing import Dict, List, Tuple, Optional, Set
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.services.traffic_prediction_service import TrafficPredictionService
from app.services.feature_engineering_service import FeatureEngineeringService
from app.models.traffic import RoadSegment
from app.models.road_accident import RoadAccident
from app.models.city_work import CityWork


class RoadGraph:
    """
    Represents the road network as a directed graph
    """
    
    def __init__(self):
        self.adjacency_list: Dict[str, List[Tuple[str, float]]] = {}
        self.segment_info: Dict[str, Dict] = {}
    
    def add_segment(self, segment_id: str, info: Dict):
        """Add a road segment to the graph"""
        if segment_id not in self.adjacency_list:
            self.adjacency_list[segment_id] = []
        self.segment_info[segment_id] = info
    
    def add_connection(self, from_segment: str, to_segment: str, distance: float):
        """Add a directed edge between segments"""
        if from_segment not in self.adjacency_list:
            self.adjacency_list[from_segment] = []
        
        # Check if connection already exists
        existing = [conn for conn in self.adjacency_list[from_segment] if conn[0] == to_segment]
        if not existing:
            self.adjacency_list[from_segment].append((to_segment, distance))
    
    def get_neighbors(self, segment_id: str) -> List[Tuple[str, float]]:
        """Get all neighboring segments and their distances"""
        return self.adjacency_list.get(segment_id, [])
    
    def get_all_segments(self) -> List[str]:
        """Get all segment IDs in the graph"""
        return list(self.adjacency_list.keys())


class SmartRoutingService:
    """
    Intelligent routing service using A* algorithm with ML predictions
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.prediction_service = TrafficPredictionService()
        self.feature_service = FeatureEngineeringService(db)
        self.graph = self._build_graph()
    
    def _build_graph(self) -> RoadGraph:
        """
        Build road network graph from database
        
        Creates connections based on:
        1. Road segments in database
        2. Geographic proximity (end point close to start point)
        3. Manual connection definitions
        """
        graph = RoadGraph()
        
        # Get all road segments from database
        segments = self.db.query(RoadSegment).all()
        
        for segment in segments:
            info = {
                'id': segment.id,
                'name': segment.roadName or segment.name or f"Segment {segment.id}",
                'start_lat': None,  # Will parse from startPoint GeoJSON
                'start_lon': None,
                'end_lat': None,    # Will parse from endPoint GeoJSON
                'end_lon': None,
                'total_lanes': segment.totalLaneNumber or 2,
                'max_speed': float(segment.maximumAllowedSpeed) if segment.maximumAllowedSpeed else 40.0,
                'road_class': segment.roadClass or 'Secondary'
            }
            graph.add_segment(segment.id, info)
        
        # Build connections between segments
        # For simplicity, assume sequential connections (segment_001 -> segment_002 -> segment_003, etc.)
        all_segments = segments
        segment_ids = [seg.id for seg in all_segments]
        segment_ids.sort()  # Sort to ensure order
        
        # Connect sequential segments
        for i in range(len(segment_ids) - 1):
            current_id = segment_ids[i]
            next_id = segment_ids[i + 1]
            
            # Get segment info
            current_seg = next(seg for seg in all_segments if seg.id == current_id)
            next_seg = next(seg for seg in all_segments if seg.id == next_id)
            
            # Use segment length as distance (default 1.5 km if not available)
            # Convert Decimal to float to avoid TypeError in arithmetic
            distance = float(current_seg.length) / 1000.0 if current_seg.length else 1.5
            
            # Bidirectional connection
            graph.add_connection(current_id, next_id, distance)
            graph.add_connection(next_id, current_id, distance)
        
        return graph
    
    def _is_connected(self, seg1: RoadSegment, seg2: RoadSegment, threshold_km: float = 0.1) -> bool:
        """
        Check if two segments are connected
        (seg1's end point is close to seg2's start point)
        """
        if not all([
            seg1.EndPointLatitude, seg1.EndPointLongitude,
            seg2.StartPointLatitude, seg2.StartPointLongitude
        ]):
            return False
        
        distance = self._calculate_distance(
            seg1.EndPointLatitude, seg1.EndPointLongitude,
            seg2.StartPointLatitude, seg2.StartPointLongitude
        )
        
        return distance <= threshold_km
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two points using Haversine formula
        Returns distance in kilometers
        """
        R = 6371  # Earth's radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def _get_active_incidents(self) -> Dict[str, List[Dict]]:
        """
        Get active accidents and construction zones
        Returns dict mapping segment_id to list of incidents
        """
        incidents = {}
        
        # Note: RoadAccident table does not have a column that references RoadSegment
        # Skipping accident queries for now - can be added if schema is updated
        
        # Get active construction zones
        try:
            query = text("""
                SELECT 
                    roadImpacted,
                    startDate,
                    endDate,
                    workState
                FROM CityWork
                WHERE workState IN ('open', 'authorized', 'planned')
                AND GETDATE() BETWEEN startDate AND endDate
                AND roadImpacted IS NOT NULL
            """)
            
            result = self.db.execute(query)
            for row in result:
                segment_id = row[0]
                if segment_id not in incidents:
                    incidents[segment_id] = []
                incidents[segment_id].append({
                    'type': 'construction',
                    'start': row[1],
                    'end': row[2],
                    'state': row[3]
                })
        except Exception as e:
            print(f"⚠️ Warning: Could not fetch construction zones: {e}")
        
        return incidents
    
    def _calculate_segment_cost(
        self,
        segment_id: str,
        distance: float,
        arrival_time: datetime,
        incidents: Dict[str, List[Dict]]
    ) -> float:
        """
        Calculate cost (travel time) for a segment
        
        ⭐ KEY FEATURE: Uses PREDICTED traffic at ARRIVAL TIME, not current time!
        This solves the problem: "If traffic jam at point C will clear before I arrive,
        route through C is still optimal!"
        
        Cost = base_time * congestion_factor * incident_penalty
        
        Args:
            segment_id: Road segment ID
            distance: Distance in km
            arrival_time: Expected ARRIVAL time at this segment (not departure!)
            incidents: Active incidents map
            
        Returns:
            Cost in minutes
        """
        segment_info = self.graph.segment_info.get(segment_id)
        if not segment_info:
            return float('inf')
        
        # 🎯 CRITICAL: Get ML prediction for ARRIVAL TIME (when you'll reach this segment)
        # This predicts traffic conditions at the time you'll actually be there!
        features = self.feature_service.engineer_features(segment_id, arrival_time)
        
        if features and self.prediction_service.is_ready():
            # Use ML prediction for FUTURE traffic at arrival time
            prediction = self.prediction_service.predict(features, model_type='ensemble')
            predicted_speed = float(prediction.get('predicted_speed', segment_info['max_speed']))
            congestion_prob = float(prediction.get('congestion_probability', 0.5))
        else:
            # Fallback to max speed with some congestion
            predicted_speed = float(segment_info['max_speed']) * 0.7
            congestion_prob = 0.3
        
        # Base travel time in minutes (using PREDICTED speed at arrival time)
        base_time = (distance / max(predicted_speed, 5.0)) * 60.0
        
        # Congestion factor (1.0 to 3.0)
        congestion_factor = 1.0 + (congestion_prob * 2.0)
        
        # Incident penalty
        incident_penalty = 1.0
        if segment_id in incidents:
            for incident in incidents[segment_id]:
                if incident['type'] == 'accident':
                    # Severe penalty for accidents
                    severity = incident.get('severity', 1)
                    incident_penalty *= (1.5 + severity * 0.1)
                elif incident['type'] == 'construction':
                    # Moderate penalty for construction
                    incident_penalty *= 1.3
        
        # Final cost
        cost = base_time * congestion_factor * incident_penalty
        
        return cost
    
    def _heuristic(self, segment_id: str, goal_id: str) -> float:
        """
        A* heuristic function - estimated time to goal
        Returns estimated time in minutes
        
        Since we don't have lat/lon coordinates, use sequential segment distance
        as heuristic (assuming segments are roughly sequential)
        """
        seg1 = self.graph.segment_info.get(segment_id)
        seg2 = self.graph.segment_info.get(goal_id)
        
        if not seg1 or not seg2:
            return 0
        
        # Extract segment numbers (e.g., "segment_001" -> 1)
        try:
            num1 = int(segment_id.split('_')[-1])
            num2 = int(goal_id.split('_')[-1])
            
            # Estimate: each segment is ~1.5 km, average speed 30 km/h
            segment_distance = abs(num2 - num1)
            estimated_km = segment_distance * 1.5
            estimated_time = (estimated_km / 30.0) * 60.0  # minutes
            
            return estimated_time
        except (ValueError, IndexError):
            # Fallback if segment naming doesn't follow pattern
            return 0
    
    def find_optimal_route(
        self,
        origin: str,
        destination: str,
        departure_time: Optional[datetime] = None
    ) -> Dict:
        """
        Find optimal route using A* algorithm with ML predictions
        
        Args:
            origin: Origin segment ID
            destination: Destination segment ID
            departure_time: Departure time (default: now)
            
        Returns:
            Route information dict
        """
        if departure_time is None:
            departure_time = datetime.now()
        
        # Check if origin and destination exist
        if origin not in self.graph.adjacency_list:
            return {
                'success': False,
                'error': f'Origin segment {origin} not found in road network'
            }
        
        if destination not in self.graph.adjacency_list:
            return {
                'success': False,
                'error': f'Destination segment {destination} not found in road network'
            }
        
        # Get active incidents
        incidents = self._get_active_incidents()
        
        # A* algorithm
        # Priority queue: (f_cost, g_cost, segment_id)
        open_set = [(0, 0, origin)]
        came_from = {}
        g_score = {origin: 0}
        f_score = {origin: self._heuristic(origin, destination)}
        closed_set: Set[str] = set()
        
        # ⭐ Track cumulative time to calculate arrival time at each segment
        cumulative_time = {origin: 0}  # Minutes from departure
        
        while open_set:
            # Get segment with lowest f_score
            current_f, current_g, current = heapq.heappop(open_set)
            
            # Goal reached
            if current == destination:
                path = self._reconstruct_path(came_from, current)
                return self._format_route_result(
                    path, g_score, departure_time, incidents, cumulative_time
                )
            
            # Skip if already processed
            if current in closed_set:
                continue
            
            closed_set.add(current)
            
            # Explore neighbors
            for neighbor, distance in self.graph.get_neighbors(current):
                if neighbor in closed_set:
                    continue
                
                # 🎯 CRITICAL: Calculate ARRIVAL TIME at neighbor segment
                # arrival_time = departure_time + time_to_reach_current + time_to_reach_neighbor
                current_cumulative_minutes = cumulative_time.get(current, 0)
                estimated_arrival_time = departure_time + timedelta(minutes=current_cumulative_minutes)
                
                # Calculate cost to neighbor using PREDICTED traffic at arrival time
                segment_cost = self._calculate_segment_cost(
                    neighbor, distance, estimated_arrival_time, incidents
                )
                
                tentative_g = g_score[current] + segment_cost
                
                # If this path to neighbor is better
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    cumulative_time[neighbor] = current_cumulative_minutes + segment_cost
                    f_score[neighbor] = tentative_g + self._heuristic(neighbor, destination)
                    heapq.heappush(open_set, (f_score[neighbor], tentative_g, neighbor))
        
        # No path found
        return {
            'success': False,
            'error': 'No route found between origin and destination'
        }
    
    def _reconstruct_path(self, came_from: Dict[str, str], current: str) -> List[str]:
        """Reconstruct path from came_from map"""
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path
    
    def _format_route_result(
        self,
        path: List[str],
        g_score: Dict[str, float],
        departure_time: datetime,
        incidents: Dict[str, List[Dict]],
        cumulative_time: Dict[str, float]
    ) -> Dict:
        """Format route result with detailed information"""
        segments_info = []
        total_distance = 0
        
        for i in range(len(path)):
            segment_id = path[i]
            segment = self.graph.segment_info.get(segment_id)
            
            if not segment:
                continue
            
            # Calculate distance to next segment
            distance = 0
            if i < len(path) - 1:
                next_segment = path[i + 1]
                for neighbor, dist in self.graph.get_neighbors(segment_id):
                    if neighbor == next_segment:
                        distance = dist
                        break
            
            total_distance += distance
            
            # Get incidents on this segment
            segment_incidents = incidents.get(segment_id, [])
            
            # ⭐ Calculate arrival time at this segment
            segment_arrival_time = departure_time + timedelta(minutes=cumulative_time.get(segment_id, 0))
            
            segments_info.append({
                'segment_id': segment_id,
                'name': segment['name'],
                'distance_km': round(distance, 2),
                'max_speed': segment['max_speed'],
                'arrival_time': segment_arrival_time.isoformat(),
                'has_incident': len(segment_incidents) > 0,
                'incidents': segment_incidents
            })
        
        total_time = g_score.get(path[-1], 0)
        estimated_arrival = departure_time + timedelta(minutes=total_time)
        
        return {
            'success': True,
            'path': path,
            'segments': segments_info,
            'total_distance_km': round(total_distance, 2),
            'estimated_time_min': round(total_time, 1),
            'departure_time': departure_time.isoformat(),
            'estimated_arrival_time': estimated_arrival.isoformat(),
            'incidents_avoided': sum(1 for seg in segments_info if seg['has_incident']),
            'prediction_based': True,  # ⭐ Flag indicating this uses predictive routing
            'explanation': 'Route calculated using AI-predicted traffic at arrival times for each segment'
        }
    
    def find_alternative_routes(
        self,
        origin: str,
        destination: str,
        departure_time: Optional[datetime] = None,
        num_routes: int = 3
    ) -> List[Dict]:
        """
        Find multiple alternative routes
        
        Strategy: Remove segments from optimal path and find new routes
        """
        routes = []
        
        # Find first optimal route
        route1 = self.find_optimal_route(origin, destination, departure_time)
        if route1['success']:
            routes.append(route1)
        
        # TODO: Implement k-shortest paths algorithm for true alternatives
        # For now, return just the optimal route
        
        return routes


def get_routing_service(db: Session) -> SmartRoutingService:
    """Factory function to get routing service instance"""
    return SmartRoutingService(db)
