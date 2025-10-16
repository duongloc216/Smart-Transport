"""
Analyze Database Schema and NULL Values
Kiểm tra tất cả các cột trong DB và đánh giá NULL values
"""

import pyodbc
import pandas as pd
from tabulate import tabulate

def get_db_connection():
    """Create database connection"""
    connection_string = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost\\MSSQLSERVER02;"
        "DATABASE=SmartTrafficDB;"
        "UID=locdt;"
        "PWD=locdt"
    )
    return pyodbc.connect(connection_string)


def analyze_table(conn, table_name):
    """Analyze một table và kiểm tra NULL values"""
    cursor = conn.cursor()
    
    print("=" * 100)
    print(f"📊 TABLE: {table_name}")
    print("=" * 100)
    
    # Get total row count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    total_rows = cursor.fetchone()[0]
    print(f"Total Rows: {total_rows}")
    print()
    
    if total_rows == 0:
        print("⚠️  Table is empty - no data to analyze")
        print()
        return [], 0
    
    # Get column information
    cursor.execute(f"""
        SELECT 
            COLUMN_NAME,
            DATA_TYPE,
            IS_NULLABLE,
            CHARACTER_MAXIMUM_LENGTH
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = '{table_name}'
        ORDER BY ORDINAL_POSITION
    """)
    
    columns_info = cursor.fetchall()
    
    # Analyze each column
    analysis_results = []
    
    for col_info in columns_info:
        col_name = col_info[0]
        data_type = col_info[1]
        is_nullable = col_info[2]
        max_length = col_info[3]
        
        # Count NULL values
        cursor.execute(f"""
            SELECT 
                COUNT(*) as total,
                COUNT({col_name}) as non_null,
                COUNT(*) - COUNT({col_name}) as null_count
            FROM {table_name}
        """)
        
        result = cursor.fetchone()
        total = result[0]
        non_null = result[1]
        null_count = result[2]
        null_percent = (null_count / total * 100) if total > 0 else 0
        
        # Get sample values (non-null)
        sample_value = None
        try:
            cursor.execute(f"""
                SELECT TOP 1 {col_name} 
                FROM {table_name} 
                WHERE {col_name} IS NOT NULL
            """)
            sample_result = cursor.fetchone()
            if sample_result:
                sample_value = str(sample_result[0])[:50]  # Limit length
        except:
            sample_value = "N/A"
        
        analysis_results.append({
            'Column': col_name,
            'Type': data_type,
            'Nullable': is_nullable,
            'Non-NULL': non_null,
            'NULL': null_count,
            'NULL %': f"{null_percent:.1f}%",
            'Sample': sample_value
        })
    
    # Display results as table
    df = pd.DataFrame(analysis_results)
    print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))
    print()
    
    # Summary
    total_columns = len(analysis_results)
    columns_with_nulls = sum(1 for r in analysis_results if r['NULL'] > 0)
    fully_null_columns = sum(1 for r in analysis_results if r['NULL'] == total_rows)
    fully_populated = sum(1 for r in analysis_results if r['NULL'] == 0)
    
    print("📈 SUMMARY:")
    print(f"  Total Columns: {total_columns}")
    print(f"  Fully Populated (0% NULL): {fully_populated}")
    print(f"  Partially NULL: {columns_with_nulls - fully_null_columns}")
    print(f"  Completely NULL (100%): {fully_null_columns}")
    print()
    
    return analysis_results, total_rows


def evaluate_null_impact(table_name, column_name, null_count, total_rows, data_type):
    """Đánh giá impact nếu cột NULL hoặc có data"""
    
    impact = {
        'column': column_name,
        'current_state': 'NULL' if null_count == total_rows else 'HAS_DATA',
        'null_percent': (null_count / total_rows * 100) if total_rows > 0 else 0,
        'importance': '',
        'if_null': '',
        'if_has_data': '',
        'recommendation': ''
    }
    
    # Define importance and impact based on column name and table
    if table_name == 'TrafficFlowObserved':
        if column_name in ['ID', 'RefRoadSegment', 'DateObservedFrom', 'AverageVehicleSpeed']:
            impact['importance'] = '🔴 CRITICAL'
            impact['if_null'] = 'System cannot function - data is useless'
            impact['if_has_data'] = 'Essential for traffic analysis and ML models'
            impact['recommendation'] = 'MUST have data - required field'
            
        elif column_name == 'Congested':
            impact['importance'] = '🔴 CRITICAL'
            impact['if_null'] = 'Cannot classify traffic conditions'
            impact['if_has_data'] = 'Enable congestion prediction and alerts'
            impact['recommendation'] = 'MUST calculate from speed and duration'
            
        elif column_name == 'Intensity':
            impact['importance'] = '🟠 HIGH'
            impact['if_null'] = 'Cannot analyze traffic volume/density'
            impact['if_has_data'] = 'Better prediction, capacity analysis, demand forecasting'
            impact['recommendation'] = 'SHOULD estimate: vehicles/hour based on speed and capacity'
            
        elif column_name == 'Occupancy':
            impact['importance'] = '🟠 HIGH'
            impact['if_null'] = 'Cannot calculate road utilization rate'
            impact['if_has_data'] = 'Optimize traffic light timing, detect bottlenecks'
            impact['recommendation'] = 'SHOULD estimate: % = (intensity / capacity) * 100'
            
        elif column_name in ['AverageGapDistance', 'AverageHeadwayTime']:
            impact['importance'] = '🟡 MEDIUM'
            impact['if_null'] = 'Less accurate safety analysis'
            impact['if_has_data'] = 'Better safety metrics, collision risk assessment'
            impact['recommendation'] = 'OPTIONAL: estimate from speed and density'
            
        elif column_name == 'AverageVehicleLength':
            impact['importance'] = '🟡 MEDIUM'
            impact['if_null'] = 'Use default value (4.5m for cars)'
            impact['if_has_data'] = 'More accurate space calculations'
            impact['recommendation'] = 'OPTIONAL: use default 4.5m for cars, 12m for buses'
            
        elif column_name == 'VehicleType':
            impact['importance'] = '🟢 LOW'
            impact['if_null'] = 'Assume mixed traffic'
            impact['if_has_data'] = 'Vehicle-specific analysis'
            impact['recommendation'] = 'OPTIONAL: default to "car" or "mixed"'
            
        elif column_name in ['LaneDirection', 'DataProvider', 'Source']:
            impact['importance'] = '🟢 LOW'
            impact['if_null'] = 'Missing metadata only'
            impact['if_has_data'] = 'Better data provenance and filtering'
            impact['recommendation'] = 'NICE TO HAVE: for documentation'
    
    elif table_name == 'RoadSegment':
        if column_name in ['ID', 'Name', 'Location', 'TotalLaneNumber']:
            impact['importance'] = '🔴 CRITICAL'
            impact['if_null'] = 'Cannot identify or use road segment'
            impact['if_has_data'] = 'Essential for routing and mapping'
            impact['recommendation'] = 'MUST have data'
            
        elif column_name == 'MaximumAllowedSpeed':
            impact['importance'] = '🟠 HIGH'
            impact['if_null'] = 'Cannot detect speeding or calculate delays'
            impact['if_has_data'] = 'Enable speed limit enforcement, delay calculation'
            impact['recommendation'] = 'SHOULD have: use default 40-50 km/h for urban'
            
        elif column_name == 'Width':
            impact['importance'] = '🟡 MEDIUM'
            impact['if_null'] = 'Estimate from lane count (lanes * 3.5m)'
            impact['if_has_data'] = 'Better capacity calculation'
            impact['recommendation'] = 'OPTIONAL: calculate from lanes'
    
    return impact


def main():
    """Main analysis function"""
    print("\n")
    print("=" * 100)
    print("🔍 DATABASE SCHEMA AND NULL VALUE ANALYSIS")
    print("=" * 100)
    print()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("""
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
    """)
    
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"📚 Found {len(tables)} tables in database")
    print(f"Tables: {', '.join(tables)}")
    print()
    
    all_impacts = []
    
    # Analyze each table
    for table in tables:
        results, total_rows = analyze_table(conn, table)
        
        if results and total_rows > 0:
            # Evaluate impact for columns with NULL
            for result in results:
                if result['NULL'] > 0:
                    impact = evaluate_null_impact(
                        table,
                        result['Column'],
                        result['NULL'],
                        total_rows,
                        result['Type']
                    )
                    if impact['importance']:  # Only if evaluation exists
                        all_impacts.append(impact)
    
    # Display impact analysis
    if all_impacts:
        print()
        print("=" * 100)
        print("💡 NULL VALUE IMPACT ANALYSIS")
        print("=" * 100)
        print()
        
        for impact in sorted(all_impacts, key=lambda x: x['importance'], reverse=True):
            print(f"{impact['importance']} {impact['column']}")
            print(f"   Current State: {impact['current_state']} ({impact['null_percent']:.1f}% NULL)")
            print(f"   ❌ If NULL: {impact['if_null']}")
            print(f"   ✅ If Has Data: {impact['if_has_data']}")
            print(f"   💡 Recommendation: {impact['recommendation']}")
            print()
    
    # Overall recommendations
    print("=" * 100)
    print("🎯 OVERALL RECOMMENDATIONS")
    print("=" * 100)
    print()
    print("🔴 CRITICAL FIELDS (Must Fix):")
    print("   1. Congested - Calculate from speed vs speed limit")
    print("   2. AverageVehicleSpeed - Already have ✅")
    print()
    print("🟠 HIGH PRIORITY (Should Fix):")
    print("   3. Intensity - Estimate vehicles/hour from speed and capacity")
    print("   4. Occupancy - Calculate as (intensity / road_capacity) * 100")
    print("   5. MaximumAllowedSpeed - Add default values (40-50 km/h)")
    print()
    print("🟡 MEDIUM PRIORITY (Nice to Have):")
    print("   6. AverageGapDistance - Estimate from speed")
    print("   7. AverageHeadwayTime - Calculate from gap distance")
    print("   8. AverageVehicleLength - Use defaults (4.5m cars, 12m buses)")
    print()
    print("🟢 LOW PRIORITY (Optional):")
    print("   9. VehicleType, LaneDirection, DataProvider - Metadata only")
    print()
    
    conn.close()


if __name__ == "__main__":
    main()
