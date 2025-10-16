"""
Seed Road Segments into Database
Loads road segments from JSON file and inserts into RoadSegment table
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent.parent / "backend"))

from app.core.database import SessionLocal
from app.models.road_segment import RoadSegment
from sqlalchemy import text


def load_road_segments_from_json(json_path: str) -> list:
    """Load road segments from JSON file"""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_geojson_linestring(origin: dict, destination: dict) -> str:
    """Create GeoJSON LineString from origin and destination"""
    return json.dumps({
        "type": "LineString",
        "coordinates": [
            [origin["lng"], origin["lat"]],
            [destination["lng"], destination["lat"]]
        ]
    })


def create_geojson_point(coord: dict) -> str:
    """Create GeoJSON Point"""
    return json.dumps({
        "type": "Point",
        "coordinates": [coord["lng"], coord["lat"]]
    })


def seed_road_segments(json_path: str = "../data/road_segments.json"):
    """
    Seed road segments from JSON file into database
    
    Args:
        json_path: Path to road_segments.json file
    """
    db = SessionLocal()
    
    try:
        print("\n" + "="*60)
        print("SEEDING ROAD SEGMENTS INTO DATABASE")
        print("="*60 + "\n")
        
        # Load segments from JSON
        segments_data = load_road_segments_from_json(json_path)
        print(f"📄 Loaded {len(segments_data)} segments from {json_path}")
        
        # Check for existing segments
        existing_count = db.query(RoadSegment).count()
        print(f"📊 Current segments in database: {existing_count}")
        
        if existing_count > 0:
            response = input("\n⚠️  Database already has segments. Clear and re-seed? (yes/no): ")
            if response.lower() == 'yes':
                db.execute(text("DELETE FROM RoadSegment"))
                db.commit()
                print("✅ Cleared existing segments")
            else:
                print("❌ Cancelled. Exiting...")
                return
        
        # Insert new segments
        inserted_count = 0
        for seg_data in segments_data:
            try:
                # Create RoadSegment model instance
                segment = RoadSegment(
                    id=seg_data["id"],
                    roadName=seg_data["name"],
                    roadClass=seg_data["road_class"],
                    description=seg_data.get("description", ""),
                    
                    # Location as GeoJSON LineString
                    location=create_geojson_linestring(
                        seg_data["origin"], 
                        seg_data["destination"]
                    ),
                    
                    # Start and end points
                    startPoint=create_geojson_point(seg_data["origin"]),
                    endPoint=create_geojson_point(seg_data["destination"]),
                    
                    # Speed and lanes
                    maximumAllowedSpeed=seg_data.get("speed_limit", 50),
                    totalLaneNumber=seg_data.get("total_lanes", 4),
                    
                    # Status
                    status="open",
                    
                    # Metadata
                    dataProvider="Manual Seed",
                    source="road_segments.json",
                    
                    # Timestamps
                    dateCreated=datetime.now(),
                    dateModified=datetime.now()
                )
                
                db.add(segment)
                inserted_count += 1
                print(f"✅ Added: {seg_data['name']}")
                
            except Exception as e:
                print(f"❌ Error adding {seg_data.get('name', 'unknown')}: {e}")
        
        # Commit all changes
        db.commit()
        
        print(f"\n" + "="*60)
        print(f"✅ SEEDING COMPLETED!")
        print(f"   Inserted: {inserted_count}/{len(segments_data)} segments")
        print("="*60 + "\n")
        
        # Verify
        final_count = db.query(RoadSegment).count()
        print(f"📊 Total segments in database: {final_count}")
        
        # Show sample
        print("\n📋 Sample segments:")
        samples = db.query(RoadSegment).limit(3).all()
        for seg in samples:
            print(f"   - {seg.id}: {seg.roadName} ({seg.roadClass}, {seg.maximumAllowedSpeed} km/h)")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        db.rollback()
    
    finally:
        db.close()


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Seed road segments into database")
    parser.add_argument(
        "--file",
        type=str,
        default="../data/road_segments.json",
        help="Path to road_segments.json file"
    )
    
    args = parser.parse_args()
    seed_road_segments(args.file)


if __name__ == "__main__":
    main()
