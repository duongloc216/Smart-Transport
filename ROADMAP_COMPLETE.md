# 📅 ROADMAP HOÀN THÀNH DỰ ÁN - CHI TIẾT

## 🎯 TỔNG QUAN TIẾN ĐỘ

### **ĐÃ HOÀN THÀNH: 70%**
- ✅ Database Setup & Data Collection (100%)
- ✅ ML Model Training & Testing (100%)
- ✅ Backend API Development (100%)
- ✅ ML Integration (100%)

### **CẦN HOÀN THÀNH: 30%**
- ⏳ Frontend Development (0%)
- ⏳ Smart Routing Implementation (0%)
- ⏳ Testing & Polish (0%)
- ⏳ Documentation & Presentation (0%)

---

## 📋 CHI TIẾT TỪNG BƯỚC

---

## **TUẦN 7-8: FRONTEND DEVELOPMENT (Ưu tiên cao)**

### **Ngày 1-2: Setup React Project**

#### **Bước 1: Create React App**
```bash
# Tạo project mới
npx create-react-app smart-traffic-frontend
cd smart-traffic-frontend

# Install dependencies
npm install leaflet react-leaflet axios recharts
npm install @mui/material @emotion/react @emotion/styled
npm install react-router-dom date-fns
```

#### **Bước 2: Project Structure**
```
smart-traffic-frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Map/
│   │   │   ├── TrafficMap.jsx          # Main map component
│   │   │   ├── SegmentMarker.jsx       # Road segment markers
│   │   │   └── TrafficLegend.jsx       # Color legend
│   │   ├── Dashboard/
│   │   │   ├── TrafficStats.jsx        # Statistics cards
│   │   │   ├── SpeedChart.jsx          # Speed time series
│   │   │   └── PredictionChart.jsx     # ML predictions
│   │   ├── Routing/
│   │   │   ├── RoutePlanner.jsx        # Route planning UI
│   │   │   └── RouteResult.jsx         # Route display
│   │   └── Layout/
│   │       ├── Navbar.jsx              # Top navigation
│   │       └── Sidebar.jsx             # Side menu
│   ├── services/
│   │   └── api.js                      # API calls
│   ├── utils/
│   │   └── helpers.js                  # Helper functions
│   ├── App.jsx
│   └── index.js
└── package.json
```

#### **Bước 3: API Service**
```javascript
// src/services/api.js
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export const trafficAPI = {
  // Get all traffic segments
  getAllTraffic: async () => {
    const response = await axios.get(`${API_BASE_URL}/traffic/realtime/all`);
    return response.data;
  },

  // Get current traffic for one segment
  getCurrentTraffic: async (segmentId) => {
    const response = await axios.get(`${API_BASE_URL}/traffic/current/${segmentId}`);
    return response.data;
  },

  // Get ML prediction
  predictTraffic: async (segmentId, horizon = 15) => {
    const response = await axios.post(`${API_BASE_URL}/traffic/predict`, {
      road_segment_id: segmentId,
      prediction_horizon: horizon,
      model_type: 'ensemble'
    });
    return response.data;
  },

  // Get history
  getHistory: async (segmentId, limit = 288) => {
    const response = await axios.get(
      `${API_BASE_URL}/traffic/history/${segmentId}?limit=${limit}`
    );
    return response.data;
  },

  // Get model info
  getModelsInfo: async () => {
    const response = await axios.get(`${API_BASE_URL}/traffic/models/info`);
    return response.data;
  }
};
```

---

### **Ngày 3-5: Map Component**

#### **TrafficMap.jsx - Main Component**
```javascript
import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, Polyline } from 'react-leaflet';
import { trafficAPI } from '../../services/api';
import 'leaflet/dist/leaflet.css';

const TrafficMap = () => {
  const [segments, setSegments] = useState([]);
  const [loading, setLoading] = useState(true);

  // HCM City center coordinates
  const center = [10.8231, 106.6297];

  // Segment coordinates (example - update with real data)
  const segmentCoordinates = {
    'segment_001': [[10.7695, 106.6578], [10.7721, 106.6634]],
    'segment_002': [[10.7721, 106.6634], [10.7748, 106.6691]],
    // ... thêm các segments khác
  };

  useEffect(() => {
    fetchTrafficData();
    const interval = setInterval(fetchTrafficData, 30000); // Update every 30s
    return () => clearInterval(interval);
  }, []);

  const fetchTrafficData = async () => {
    try {
      const data = await trafficAPI.getAllTraffic();
      setSegments(data.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching traffic:', error);
    }
  };

  const getColorByCongestion = (status) => {
    const colors = {
      'FREE_FLOW': '#00ff00',        // Green
      'MODERATE': '#ffff00',         // Yellow
      'HEAVY_CONGESTION': '#ff0000'  // Red
    };
    return colors[status] || '#999999';
  };

  return (
    <div style={{ height: '100vh', width: '100%' }}>
      <MapContainer 
        center={center} 
        zoom={13} 
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; OpenStreetMap contributors'
        />

        {segments.map((segment) => {
          const coords = segmentCoordinates[segment.road_segment_id];
          const color = getColorByCongestion(segment.congestion_status);

          return coords ? (
            <Polyline
              key={segment.road_segment_id}
              positions={coords}
              color={color}
              weight={6}
              opacity={0.7}
            >
              <Popup>
                <div>
                  <h3>{segment.road_name}</h3>
                  <p><strong>Speed:</strong> {segment.speed.toFixed(1)} km/h</p>
                  <p><strong>Intensity:</strong> {segment.intensity.toFixed(0)} veh/h</p>
                  <p><strong>Status:</strong> {segment.congestion_status}</p>
                  <p><strong>Congestion:</strong> {(segment.congestion_probability * 100).toFixed(0)}%</p>
                </div>
              </Popup>
            </Polyline>
          ) : null;
        })}
      </MapContainer>

      {loading && (
        <div style={{ position: 'absolute', top: 20, right: 20, background: 'white', padding: 10 }}>
          Loading traffic data...
        </div>
      )}
    </div>
  );
};

export default TrafficMap;
```

---

### **Ngày 6-7: Dashboard Components**

#### **TrafficStats.jsx - Statistics Cards**
```javascript
import React, { useState, useEffect } from 'react';
import { Card, CardContent, Typography, Grid } from '@mui/material';
import { trafficAPI } from '../../services/api';

const TrafficStats = () => {
  const [stats, setStats] = useState({
    totalSegments: 0,
    congested: 0,
    moderate: 0,
    freeFlow: 0,
    avgSpeed: 0
  });

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchStats = async () => {
    try {
      const data = await trafficAPI.getAllTraffic();
      const segments = data.data;

      const congested = segments.filter(s => s.congestion_status === 'HEAVY_CONGESTION').length;
      const moderate = segments.filter(s => s.congestion_status === 'MODERATE').length;
      const freeFlow = segments.filter(s => s.congestion_status === 'FREE_FLOW').length;
      const avgSpeed = segments.reduce((sum, s) => sum + s.speed, 0) / segments.length;

      setStats({
        totalSegments: segments.length,
        congested,
        moderate,
        freeFlow,
        avgSpeed: avgSpeed.toFixed(1)
      });
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>
              Total Segments
            </Typography>
            <Typography variant="h4">
              {stats.totalSegments}
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card style={{ backgroundColor: '#ffebee' }}>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>
              🔴 Congested
            </Typography>
            <Typography variant="h4">
              {stats.congested}
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card style={{ backgroundColor: '#fff9c4' }}>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>
              🟡 Moderate
            </Typography>
            <Typography variant="h4">
              {stats.moderate}
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card style={{ backgroundColor: '#e8f5e9' }}>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>
              🟢 Free Flow
            </Typography>
            <Typography variant="h4">
              {stats.freeFlow}
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>
              Average Speed
            </Typography>
            <Typography variant="h4">
              {stats.avgSpeed} km/h
            </Typography>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export default TrafficStats;
```

#### **SpeedChart.jsx - Time Series Chart**
```javascript
import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { trafficAPI } from '../../services/api';
import { format } from 'date-fns';

const SpeedChart = ({ segmentId }) => {
  const [data, setData] = useState([]);

  useEffect(() => {
    if (segmentId) {
      fetchHistory();
    }
  }, [segmentId]);

  const fetchHistory = async () => {
    try {
      const response = await trafficAPI.getHistory(segmentId, 48); // Last 4 hours
      const formatted = response.data.map(d => ({
        time: format(new Date(d.timestamp), 'HH:mm'),
        speed: d.speed,
        intensity: d.intensity / 100 // Scale down for visualization
      }));
      setData(formatted.reverse()); // Oldest to newest
    } catch (error) {
      console.error('Error fetching history:', error);
    }
  };

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="time" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="speed" stroke="#8884d8" name="Speed (km/h)" />
        <Line type="monotone" dataKey="intensity" stroke="#82ca9d" name="Intensity (x100 veh/h)" />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default SpeedChart;
```

---

### **Ngày 8: Integration & Testing**

#### **App.jsx - Main Application**
```javascript
import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Container } from '@mui/material';
import Navbar from './components/Layout/Navbar';
import TrafficMap from './components/Map/TrafficMap';
import TrafficStats from './components/Dashboard/TrafficStats';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Navbar />
        <Routes>
          <Route path="/" element={
            <>
              <Container maxWidth="xl" style={{ marginTop: 20 }}>
                <TrafficStats />
              </Container>
              <TrafficMap />
            </>
          } />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
```

#### **Test Frontend**
```bash
# Start frontend
npm start

# Should open http://localhost:3000
# Ensure backend is running on http://localhost:8000
```

---

## **TUẦN 9: SMART ROUTING (30% công việc còn lại)**

### **Ngày 1-3: Routing Algorithm Backend**

#### **routing_service.py**
```python
"""
Smart Routing Service
A* algorithm with ML-predicted traffic weights
"""

import networkx as nx
from typing import List, Dict, Tuple
from datetime import datetime

from app.services.traffic_prediction_service import get_prediction_service
from app.services.feature_engineering_service import FeatureEngineeringService


class SmartRoutingService:
    """
    Intelligent routing using A* algorithm with ML predictions
    """
    
    def __init__(self, db):
        self.db = db
        self.ml_service = get_prediction_service()
        self.feature_service = FeatureEngineeringService(db)
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """Build road network graph"""
        G = nx.DiGraph()
        
        # Add segments as edges
        # TODO: Query RoadSegment table for connections
        segments = [
            ('segment_001', 'segment_002', 1.5),  # (from, to, distance_km)
            ('segment_002', 'segment_003', 1.2),
            # ... Add all connections
        ]
        
        for from_seg, to_seg, distance in segments:
            G.add_edge(from_seg, to_seg, distance=distance)
        
        return G
    
    def find_optimal_route(
        self,
        origin: str,
        destination: str,
        departure_time: datetime = None
    ) -> Dict:
        """
        Find optimal route using A* with ML predictions
        """
        if departure_time is None:
            departure_time = datetime.now()
        
        # Get ML predictions for all segments
        segment_weights = {}
        for segment_id in self.graph.nodes():
            features = self.feature_service.engineer_features(
                segment_id, 
                departure_time
            )
            if features:
                prediction = self.ml_service.predict(features)
                # Weight = distance / speed (travel time)
                # Higher congestion = higher weight
                speed = prediction['predicted_speed']
                congestion_factor = 1 + prediction['congestion_probability']
                segment_weights[segment_id] = congestion_factor / max(speed, 5)
        
        # Update graph weights
        for u, v, data in self.graph.edges(data=True):
            distance = data['distance']
            weight = segment_weights.get(v, 1.0)
            self.graph[u][v]['weight'] = distance * weight
        
        # Find shortest path (A* algorithm)
        try:
            path = nx.astar_path(
                self.graph,
                origin,
                destination,
                weight='weight'
            )
            
            # Calculate route stats
            total_distance = 0
            total_time = 0
            segments_info = []
            
            for i in range(len(path) - 1):
                u, v = path[i], path[i+1]
                edge_data = self.graph[u][v]
                distance = edge_data['distance']
                weight = edge_data['weight']
                
                total_distance += distance
                total_time += weight
                
                segments_info.append({
                    'segment_id': v,
                    'distance_km': distance,
                    'estimated_time_min': weight * 60
                })
            
            return {
                'success': True,
                'path': path,
                'segments': segments_info,
                'total_distance_km': total_distance,
                'estimated_time_min': total_time * 60,
                'departure_time': departure_time
            }
            
        except nx.NetworkXNoPath:
            return {
                'success': False,
                'error': 'No route found between origin and destination'
            }
```

### **Ngày 4-5: Routing API Endpoints**

Update `routing.py`:
```python
@router.post("/optimize", response_model=RouteResponse)
async def find_optimal_route(
    request: RouteRequest,
    db: Session = Depends(get_db)
):
    """
    Tìm đường đi tối ưu tránh kẹt xe
    
    Uses A* algorithm with ML-predicted traffic conditions
    """
    try:
        routing_service = SmartRoutingService(db)
        result = routing_service.find_optimal_route(
            origin=request.origin,
            destination=request.destination,
            departure_time=request.departure_time
        )
        
        if not result['success']:
            raise HTTPException(status_code=404, detail=result['error'])
        
        return RouteResponse(
            success=True,
            origin=request.origin,
            destination=request.destination,
            routes=[{
                'path': result['path'],
                'segments': result['segments'],
                'total_distance': result['total_distance_km'],
                'estimated_time': result['estimated_time_min']
            }],
            generated_at=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## **TUẦN 10: TESTING & POLISH (20% công việc còn lại)**

### **Day 1-2: Backend Testing**
```python
# tests/test_traffic_api.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_current_traffic():
    response = client.get("/api/v1/traffic/current/segment_001")
    assert response.status_code == 200
    data = response.json()
    assert data['success'] == True
    assert 'speed' in data

def test_predict_traffic():
    response = client.post("/api/v1/traffic/predict", json={
        "road_segment_id": "segment_001",
        "prediction_horizon": 15
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data['predictions']) > 0

# Run: pytest tests/
```

### **Day 3-4: Frontend Testing**
```bash
# Install testing library
npm install --save-dev @testing-library/react @testing-library/jest-dom

# Create tests
# src/components/__tests__/TrafficMap.test.js
```

### **Day 5: Performance Optimization**
- Add Redis caching for API responses
- Optimize database queries
- Compress API responses
- Add loading skeletons

---

## **TUẦN 11: DEPLOYMENT (10% công việc còn lại)**

### **Docker Setup**

#### **backend/Dockerfile**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### **frontend/Dockerfile**
```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

RUN npm run build

FROM nginx:alpine
COPY --from=0 /app/build /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

#### **docker-compose.yml**
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DB_SERVER=sqlserver
      - DB_NAME=SmartTrafficDB
    depends_on:
      - sqlserver

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

  sqlserver:
    image: mcr.microsoft.com/mssql/server:2022-latest
    environment:
      - ACCEPT_EULA=Y
      - SA_PASSWORD=YourPassword123!
    ports:
      - "1433:1433"
```

### **Deploy to Cloud**
```bash
# Option 1: DigitalOcean
doctl apps create --spec .do/app.yaml

# Option 2: AWS EC2
# Upload docker-compose.yml and run
docker-compose up -d

# Option 3: Azure
az container create --resource-group smart-traffic --file docker-compose.yml
```

---

## **TUẦN 12: DOCUMENTATION & PRESENTATION**

### **Day 1-3: Technical Documentation**
```markdown
# docs/TECHNICAL_DOCUMENTATION.md

## Architecture Overview
## API Reference
## ML Models Explanation
## Database Schema
## Deployment Guide
```

### **Day 4-5: User Guide**
```markdown
# docs/USER_GUIDE.md

## How to Use the System
## Understanding Traffic Colors
## Route Planning Tutorial
## FAQ
```

### **Day 6-7: Presentation**
- Create PowerPoint slides
- Prepare demo video
- Practice presentation
- Q&A preparation

---

## 📊 CHECKLIST TỔNG QUÁT

### **Frontend**
- [ ] Map visualization với traffic colors
- [ ] Real-time updates (30s interval)
- [ ] Dashboard với statistics
- [ ] Speed charts (time series)
- [ ] Prediction visualization
- [ ] Responsive design (mobile-friendly)

### **Backend**
- [ ] 5 traffic endpoints hoạt động ✅
- [ ] Smart routing endpoint
- [ ] API documentation (Swagger) ✅
- [ ] Error handling
- [ ] Caching (Redis)
- [ ] Rate limiting

### **ML**
- [ ] Models trained & tested ✅
- [ ] Integration with API ✅
- [ ] Feature engineering ✅
- [ ] Model versioning
- [ ] Monitoring accuracy

### **Testing**
- [ ] Unit tests (backend)
- [ ] Integration tests
- [ ] Frontend tests
- [ ] Performance tests
- [ ] Load testing

### **Deployment**
- [ ] Docker containers
- [ ] docker-compose setup
- [ ] Cloud deployment
- [ ] CI/CD pipeline
- [ ] Monitoring (Grafana)

### **Documentation**
- [ ] Technical docs
- [ ] User guide
- [ ] API reference ✅
- [ ] README.md
- [ ] Presentation slides

---

## 🎯 PRIORITIES

### **MUST HAVE (Bắt buộc):**
1. ✅ Backend API với ML predictions
2. ⏳ Frontend map với traffic visualization
3. ⏳ Dashboard với real-time stats
4. ⏳ Basic routing functionality

### **SHOULD HAVE (Nên có):**
5. ⏳ Advanced charts & analytics
6. ⏳ Historical data visualization
7. ⏳ Smart routing với ML
8. ⏳ Mobile responsive

### **NICE TO HAVE (Tốt nếu có):**
9. ⏳ User authentication
10. ⏳ Admin dashboard
11. ⏳ Email notifications
12. ⏳ Export reports

---

## ⏱️ ESTIMATED TIMELINE

| Week | Task | Hours | Status |
|------|------|-------|--------|
| 1-6 | Backend + ML | 60h | ✅ DONE |
| 7-8 | Frontend Dev | 40h | ⏳ TODO |
| 9 | Smart Routing | 20h | ⏳ TODO |
| 10 | Testing | 15h | ⏳ TODO |
| 11 | Deployment | 10h | ⏳ TODO |
| 12 | Documentation | 15h | ⏳ TODO |
| **Total** | | **160h** | **70% Done** |

---

## 🚀 IMMEDIATE NEXT STEPS (3 NGÀY TỚI)

### **Ngày 1: Setup Frontend**
```bash
# 1. Create React app
npx create-react-app smart-traffic-frontend
cd smart-traffic-frontend

# 2. Install dependencies
npm install leaflet react-leaflet axios @mui/material recharts

# 3. Create folder structure
mkdir -p src/components/{Map,Dashboard,Layout}
mkdir -p src/services
```

### **Ngày 2: Build Map Component**
- Implement TrafficMap.jsx
- Add Leaflet map
- Connect to `/realtime/all` API
- Color-code segments by congestion

### **Ngày 3: Build Dashboard**
- TrafficStats.jsx (statistics cards)
- SpeedChart.jsx (time series)
- Connect to API
- Real-time updates

---

## 📝 SUMMARY

**Bạn cần:**
1. **Frontend (2 tuần)** - Map + Dashboard + Charts
2. **Smart Routing (1 tuần)** - A* algorithm với ML
3. **Testing (1 tuần)** - Unit tests + Integration tests
4. **Deployment (1 tuần)** - Docker + Cloud
5. **Documentation (1 tuần)** - Docs + Presentation

**Total: 6 tuần (30% còn lại)**

**Ưu tiên cao nhất:** Frontend Development (Map + Dashboard)

---

Bạn muốn tôi:
1. ✅ Tạo code template cho Frontend ngay?
2. ✅ Giải thích chi tiết từng component?
3. ✅ Tạo Smart Routing backend?
4. ✅ Setup Docker deployment?

**Chọn một để tôi bắt đầu giúp bạn! 🚀**
