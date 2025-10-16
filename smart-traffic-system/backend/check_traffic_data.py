import pyodbc

# Connect to database
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost\\MSSQLSERVER02;'
    'DATABASE=SmartTrafficDB;'
    'UID=locdt;'
    'PWD=locdt'
)

cursor = conn.cursor()

# Count total records
cursor.execute('SELECT COUNT(*) FROM TrafficFlowObserved')
total = cursor.fetchone()[0]
print(f'\n📊 Total Traffic Records: {total}')

# Get latest 5 records
cursor.execute('''
    SELECT TOP 5 
        ID, 
        RefRoadSegment, 
        AverageVehicleSpeed, 
        Congested, 
        DateObservedFrom 
    FROM TrafficFlowObserved 
    ORDER BY DateObservedFrom DESC
''')

print('\n🕐 Latest 5 Records:')
print('-' * 80)
for row in cursor.fetchall():
    status = '🔴 CONGESTED' if row[3] else '🟢 FLOWING'
    print(f'{row[0][:35]}... | {row[2]:6.2f} km/h | {status} | {row[4]}')

conn.close()
print('-' * 80)
