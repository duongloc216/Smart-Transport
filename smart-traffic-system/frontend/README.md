# Smart Traffic Frontend

React-based dashboard for visualizing real-time traffic and route planning.

## 🚀 Quick Start

### Install Dependencies

```bash
npm install
```

### Run Development Server

```bash
npm run dev
```

Visit: http://localhost:3000

### Build for Production

```bash
npm run build
```

## 📦 Tech Stack

- **React 18** - UI Framework
- **Vite** - Build tool
- **Leaflet** - Interactive maps
- **Axios** - HTTP client
- **Recharts** - Data visualization

## 🗂️ Project Structure

```
src/
├── components/
│   ├── Map/
│   │   ├── TrafficMap.jsx        # Main map component
│   │   └── TrafficMap.css
│   └── Dashboard/
│       ├── TrafficStats.jsx      # Statistics cards
│       └── TrafficStats.css
├── services/
│   └── api.js                    # API client
├── utils/
│   └── helpers.js                # Helper functions
├── App.jsx                       # Main app
├── App.css
├── main.jsx                      # Entry point
└── index.css
```

## 🔧 Configuration

Create `.env` file:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

## 🎨 Features

### 1. Real-time Traffic Map
- 🗺️ Interactive Leaflet map
- 🚦 Color-coded traffic segments
- 📊 Live traffic statistics
- ⚡ Auto-refresh every 30s

### 2. Traffic Statistics
- 📈 Total segments
- 🔴 Congested roads count
- 🟡 Moderate traffic
- 🟢 Free-flowing roads
- ⚡ Average speed
- 🚗 Total intensity

### 3. Route Planning (Coming Soon)
- 📍 Origin/Destination input
- 🛣️ Optimal route display
- 🔀 Alternative routes
- ⏱️ ETA calculation

## 🌐 API Integration

Frontend connects to FastAPI backend:

- `GET /api/v1/traffic/realtime/all` - All traffic data
- `GET /api/v1/traffic/current/:id` - Segment traffic
- `GET /api/v1/traffic/history/:id` - Historical data
- `POST /api/v1/traffic/predict` - ML predictions
- `POST /api/v1/routing/find-route` - Find route

## 📱 Responsive Design

- ✅ Desktop (1200px+)
- ✅ Tablet (768px - 1200px)
- ✅ Mobile (< 768px)

## 🚧 Development

### Add New Component

```bash
# Create component folder
mkdir src/components/NewComponent

# Create files
touch src/components/NewComponent/NewComponent.jsx
touch src/components/NewComponent/NewComponent.css
```

### Debug Mode

```bash
npm run dev -- --debug
```

## 📄 License

MIT
