# 🐳 Docker Deployment Guide

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/duongloc216/Smart-Transport.git
cd Smart-Transport/smart-traffic-system
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
# Minimum required: DB_PASSWORD
```

### 3. Start All Services

```bash
# Build and start all containers
docker-compose up -d

# View logs
docker-compose logs -f
```

### 4. Initialize Database

```bash
# Wait for SQL Server to be ready
sleep 30

# Run database schema
docker exec -it smart-traffic-db /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "YourStrong@Passw0rd" -i /path/to/create_all.sql
```

### 5. Access Application

- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs

## 📦 Services

### Backend (FastAPI)
- **Port**: 8000
- **Health**: http://localhost:8000/health
- **Container**: smart-traffic-backend

### Frontend (React + Nginx)
- **Port**: 80
- **Container**: smart-traffic-frontend

### Database (SQL Server)
- **Port**: 1433
- **Container**: smart-traffic-db
- **Volume**: sqlserver_data

### Redis (Caching)
- **Port**: 6379
- **Container**: smart-traffic-redis
- **Volume**: redis_data

## 🔧 Management Commands

### View Status

```bash
docker-compose ps
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Restart Services

```bash
# All services
docker-compose restart

# Specific service
docker-compose restart backend
```

### Stop Services

```bash
docker-compose stop
```

### Remove Containers

```bash
# Stop and remove containers
docker-compose down

# Remove containers and volumes
docker-compose down -v
```

### Rebuild

```bash
# Rebuild specific service
docker-compose build backend

# Rebuild all
docker-compose build

# Rebuild and restart
docker-compose up -d --build
```

## 📊 Database Management

### Access SQL Server

```bash
docker exec -it smart-traffic-db /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "YourStrong@Passw0rd"
```

### Backup Database

```bash
docker exec smart-traffic-db /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "YourStrong@Passw0rd" -Q "BACKUP DATABASE SmartTrafficDB TO DISK = '/var/opt/mssql/backup/smart_traffic.bak'"
```

### Restore Database

```bash
docker exec smart-traffic-db /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "YourStrong@Passw0rd" -Q "RESTORE DATABASE SmartTrafficDB FROM DISK = '/var/opt/mssql/backup/smart_traffic.bak'"
```

## 🚀 Production Deployment

### Environment Variables

```bash
# .env for production
DEBUG=false
DB_PASSWORD=<strong-password>
CORS_ORIGINS=https://yourdomain.com
```

### SSL/HTTPS Setup

```yaml
# docker-compose.prod.yml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx/ssl:/etc/nginx/ssl
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
```

### Scaling

```bash
# Scale backend instances
docker-compose up -d --scale backend=3
```

## 🐛 Troubleshooting

### Backend won't start

```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. Database not ready - wait longer
# 2. Port 8000 in use - change port in docker-compose.yml
# 3. Environment variables - check .env file
```

### Frontend 502 Error

```bash
# Check backend is running
curl http://localhost:8000/health

# Check nginx config
docker exec smart-traffic-frontend nginx -t

# Restart frontend
docker-compose restart frontend
```

### Database connection failed

```bash
# Check SQL Server is running
docker-compose ps sqlserver

# Check connection
docker exec smart-traffic-db /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "YourStrong@Passw0rd" -Q "SELECT 1"

# Check environment variables
docker-compose config
```

## 📈 Monitoring

### Resource Usage

```bash
docker stats
```

### Health Checks

```bash
# Backend
curl http://localhost:8000/health

# Frontend
curl http://localhost/

# Database
docker exec smart-traffic-db /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "YourStrong@Passw0rd" -Q "SELECT 1"
```

## 🔄 Updates

### Pull Latest Code

```bash
git pull origin main
docker-compose down
docker-compose build
docker-compose up -d
```

### Update Single Service

```bash
# Update backend
docker-compose build backend
docker-compose up -d backend

# Update frontend
docker-compose build frontend
docker-compose up -d frontend
```

## 💾 Data Persistence

Volumes are used for data persistence:

- `sqlserver_data` - Database files
- `redis_data` - Cache data

Data persists even when containers are removed (unless using `docker-compose down -v`)

## 🌐 Cloud Deployment

### AWS ECS

```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker-compose build
docker-compose push
```

### Azure Container Instances

```bash
az container create --resource-group smart-traffic --file docker-compose.yml
```

### Google Cloud Run

```bash
gcloud run deploy smart-traffic-backend --source ./backend
gcloud run deploy smart-traffic-frontend --source ./frontend
```

## 📄 License

MIT
