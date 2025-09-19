# 🛡️ Smart Tourist Safety Monitoring & Incident Response System

A comprehensive real-time emergency operations platform designed to monitor tourist safety, detect anomalies, and coordinate emergency responses using advanced AI-powered analytics and geospatial tracking.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Demo Data](#demo-data)
- [API Documentation](#api-documentation)
- [System Components](#system-components)
- [Troubleshooting](#troubleshooting)
- [Technology Stack](#technology-stack)
- [Contributing](#contributing)

## 🎯 Overview

The Smart Tourist Safety Monitoring System is an operator-focused emergency response platform that provides real-time monitoring, AI-powered anomaly detection, and coordinated incident response capabilities for tourism safety operations.

### Key Capabilities

- **Real-time Location Tracking** with WebSocket communication
- **AI-Powered Anomaly Detection** for route deviation and prolonged inactivity  
- **Geo-fencing & Breach Detection** with MongoDB geospatial queries
- **Centralized Alert Management** with panic button integration
- **Emergency Operations Dashboard** optimized for quick decision-making
- **Digital Identity Management** with blockchain-inspired audit trails
- **Multi-role Authentication** for different operator types

## ✨ Features

### 🚨 Real-time Monitoring & Alerts
- Live location tracking with WebSocket updates
- Panic button with immediate alert broadcasting  
- Geofence breach detection with risk assessment
- Route deviation monitoring (>2km threshold)
- Prolonged inactivity detection (>90min threshold)
- Multi-level alert status management (NEW → IN_PROGRESS → RESOLVED)

### 🤖 AI-Powered Analytics  
- Background anomaly detection service
- Dynamic safety score calculation
- Risk factor analysis and trend detection
- Predictive route monitoring
- Automated alert generation

### 🗺️ Advanced Geospatial Features
- Interactive live map with tourist markers
- Real-time trail visualization
- MongoDB geospatial queries with $geoIntersects
- Custom geofence management
- Location history tracking

### 👨‍💼 Operator-Focused Interface
- Emergency operations dashboard design
- High-contrast, low-cognitive-load UI
- Three-column layout for optimal information hierarchy
- Prominent status badges and safety scores
- Quick-access response action buttons

### 🔐 Security & Privacy
- Encrypted sensitive data storage
- Digital ID verification system  
- Role-based access control
- Immutable audit logging
- Emergency data access protocols

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Digital ID    │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   Service       │
│   Port: 3000    │    │   Port: 8001    │    │   Port: 8002    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────►│    MongoDB      │◄─────────────┘
                        │   Port: 27017   │
                        └─────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     WebSocket Connections                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │  Location   │  │  Dashboard  │  │   Alerts    │            │
│  │  Updates    │  │   Updates   │  │ Broadcasting│            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 Prerequisites

### Required Software
- **Node.js** (v16 or higher)
- **Python** (v3.8 or higher)  
- **MongoDB** (v4.4 or higher)
- **Git**

### System Requirements
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **OS**: Windows 10+, macOS 10.15+, or Linux Ubuntu 18.04+

## 📥 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/smart-tourist-safety-system.git
cd smart-tourist-safety-system
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory  
cd ../frontend

# Install dependencies (using yarn - required)
yarn install
```

### 4. Digital ID Service Setup

```bash
# Navigate to digital ID service directory
cd ../digital_id_service

# Install dependencies
pip install -r requirements.txt
```

### 5. Database Setup

```bash
# Start MongoDB service
# On Windows:
net start MongoDB

# On macOS (with Homebrew):
brew services start mongodb/brew/mongodb-community

# On Linux:
sudo systemctl start mongod
```

## ⚙️ Configuration

### 1. Backend Environment Variables

Create `/backend/.env`:

```env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="tourist_safety_db"
CORS_ORIGINS="*"

# Digital ID Service Configuration
DIGITAL_ID_SERVICE_URL="http://localhost:8002"
DIGITAL_ID_SERVICE_API_KEY="secure_service_api_key_production_123"
```

### 2. Frontend Environment Variables

Create `/frontend/.env`:

```env
REACT_APP_BACKEND_URL=http://localhost:8001
WDS_SOCKET_PORT=3000
```

### 3. Digital ID Service Environment Variables

Create `/digital_id_service/.env`:

```env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="digital_id_service_db"
SERVICE_API_KEY="secure_service_api_key_production_123"
```

## 🚀 Running the Application

### Method 1: Manual Start (Development)

#### Terminal 1: Start Backend
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python server.py
```

#### Terminal 2: Start Frontend
```bash
cd frontend
yarn start
```

#### Terminal 3: Start Digital ID Service
```bash
cd digital_id_service
python server.py
```

#### Terminal 4: Initialize Demo Data
```bash
cd backend
MONGO_URL="mongodb://localhost:27017" DB_NAME="tourist_safety_db" python init_data.py
```

### Method 2: Using Process Manager (Production-like)

```bash
# Install supervisord
pip install supervisor

# Start all services
supervisord -c supervisord.conf
supervisorctl start all
```

### 🌐 Access the Application

- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **Digital ID Service**: http://localhost:8002
- **API Documentation**: http://localhost:8001/docs

## 🎭 Demo Data

### Demo User Accounts

| Role | Email | Password | Access Level |
|------|-------|----------|--------------|
| Police Inspector | inspector.kumar@tourism.gov.in | password123 | Full Access |
| Tourism Admin | admin.singh@tourism.gov.in | admin123 | Admin Access |
| Field Officer | officer.sharma@tourism.gov.in | officer123 | Limited Access |

### Demo Tourist Scenarios

1. **🆘 Raj Verma (DIG-PANIC01)** - Active panic alert scenario
2. **🚫 Emily Carter (DIG-BREACH02)** - Geofence breach in restricted area  
3. **🗺️ Priya Sharma (DIG-DEVIATE03)** - Route deviation detection
4. **✅ John Doe (DIG-SAFE04)** - Safe status with data privacy
5. **📋 Aisha Khan (DIG-RESOLVED05)** - Resolved incident history

### Initializing Demo Data

```bash
cd backend
python init_data.py
```

This creates:
- 3 demo officer accounts
- 5 tourist scenarios with different risk profiles
- 3 geofenced areas (Military Zone, Forest Area, Safe Zone)
- 4 demo alerts with various statuses
- Location history data for realistic trails

## 📚 API Documentation

### Authentication Endpoints

```bash
# Login
POST /api/auth/login
Content-Type: application/json
{
  "email": "inspector.kumar@tourism.gov.in",
  "password": "password123"
}

# Get current user
GET /api/auth/me
Authorization: Bearer <token>
```

### Tourist Management

```bash
# Get all tourists
GET /api/tourists
Authorization: Bearer <token>

# Get specific tourist
GET /api/tourists/{tourist_id}
Authorization: Bearer <token>

# Get tourist alerts
GET /api/tourists/{tourist_id}/alerts
Authorization: Bearer <token>
```

### Real-time Features

```bash
# WebSocket Location Updates
WS /api/ws/location/{tourist_id}

# WebSocket Dashboard Updates  
WS /api/ws/dashboard

# Get live locations
GET /api/location/live
Authorization: Bearer <token>
```

### Alert Management

```bash
# Create panic alert
POST /api/alerts/panic
Authorization: Bearer <token>
{
  "tourist_id": "string",
  "location": {...}
}

# Get dashboard KPIs
GET /api/analytics/dashboard
Authorization: Bearer <token>
```

### AI & Analytics

```bash
# Get safety score
GET /api/ai/safety-score/{tourist_id}
Authorization: Bearer <token>

# Trigger anomaly check
POST /api/ai/anomaly-check/{tourist_id}
Authorization: Bearer <token>

# Background task status
GET /api/ai/background-tasks/status
Authorization: Bearer <token>
```

## 🔧 System Components

### Backend Services (`/backend/`)

- **`server.py`** - Main FastAPI server with all endpoints
- **`auth.py`** - JWT authentication and user management
- **`database.py`** - MongoDB connection and operations
- **`models.py`** - Pydantic models for data validation
- **`websocket_manager.py`** - WebSocket connection management
- **`background_tasks.py`** - Background task management for AI

### Service Layer (`/backend/services/`)

- **`tourist_service.py`** - Tourist data operations
- **`alert_service.py`** - Alert creation and management
- **`location_service.py`** - Location tracking and history
- **`geofence_service.py`** - Geospatial queries and breach detection
- **`anomaly_service.py`** - AI-powered anomaly detection
- **`digital_id_client.py`** - Digital ID service integration

### Frontend Components (`/frontend/src/`)

- **`pages/LiveMap.jsx`** - Real-time map with tourist locations
- **`pages/TouristDatabase.jsx`** - Tourist registry and search
- **`components/TouristDetailModal.jsx`** - Detailed tourist report (redesigned)
- **`services/api.js`** - API client with authentication
- **`contexts/AuthContext.jsx`** - Authentication state management

### Digital ID Service (`/digital_id_service/`)

- **`server.py`** - Microservice for digital identity management
- **`services/blockchain_service.py`** - Blockchain-inspired audit logging
- **`services/encryption_service.py`** - AES encryption for sensitive data

## 🐛 Troubleshooting

### Common Issues

#### 1. Backend Won't Start
```bash
# Check if MongoDB is running
mongosh --eval "db.runCommand({connectionStatus : 1})"

# Install missing dependencies
pip install httpcore

# Check environment variables
echo $MONGO_URL
```

#### 2. Frontend Build Errors
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
yarn install

# Check React version compatibility
yarn list react
```

#### 3. Authentication Issues
```bash
# Reinitialize demo data
cd backend
python init_data.py

# Test login endpoint
curl -X POST "http://localhost:8001/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "inspector.kumar@tourism.gov.in", "password": "password123"}'
```

#### 4. WebSocket Connection Problems
```bash
# Check WebSocket endpoint
curl -i -N -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" \
  -H "Sec-WebSocket-Key: demo" \
  http://localhost:8001/api/ws/dashboard
```

#### 5. Database Connection Issues
```bash
# Test MongoDB connection
mongosh mongodb://localhost:27017/tourist_safety_db

# Check collections exist
db.tourists.countDocuments()
db.users.countDocuments()
```

### Performance Optimization

```bash
# Create MongoDB indexes for better performance
mongosh mongodb://localhost:27017/tourist_safety_db
db.location_history.createIndex({"location.coordinates": "2dsphere"})
db.tourists.createIndex({"status": 1})
db.alerts.createIndex({"tourist_id": 1, "status": 1})
```

### Logging and Monitoring

```bash
# Backend logs
tail -f backend/logs/app.log

# Frontend development logs
yarn start --verbose

# Database logs
tail -f /var/log/mongodb/mongod.log
```

## 💻 Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **MongoDB** - NoSQL database with geospatial support
- **Motor** - Async MongoDB driver
- **PyJWT** - JSON Web Token implementation
- **WebSockets** - Real-time communication
- **Pydantic** - Data validation and serialization
- **Passlib** - Password hashing
- **HTTPCore** - Async HTTP client

### Frontend  
- **React 18** - Modern UI framework
- **React Router** - Client-side routing
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Icon library
- **Axios** - HTTP client
- **WebSocket API** - Real-time updates

### Database & Infrastructure
- **MongoDB** - Primary database with geospatial indexes
- **Docker** - Containerization (optional)
- **Supervisor** - Process management
- **CORS** - Cross-origin resource sharing

### AI & Analytics
- **Custom Algorithms** - Route deviation detection
- **Geospatial Analysis** - MongoDB $geoIntersects queries
- **Background Tasks** - Async anomaly monitoring
- **Safety Scoring** - Risk assessment algorithms

## 🤝 Contributing

### Development Workflow

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-feature`
3. **Make changes and test thoroughly**
4. **Update documentation if needed**
5. **Submit pull request with detailed description**

### Code Standards

- **Python**: Follow PEP 8 style guidelines
- **JavaScript**: Use ESLint and Prettier
- **Commit Messages**: Use conventional commit format
- **Testing**: Include unit tests for new features

### Testing

```bash
# Backend tests
cd backend
python -m pytest tests/

# Frontend tests  
cd frontend
yarn test

# Integration tests
python comprehensive_test.py
```

---

## 📞 Support

For technical support or questions:

- **Issues**: Create GitHub issue with detailed description
- **Documentation**: Check `/docs` folder for detailed guides
- **API Reference**: Available at http://localhost:8001/docs when running

---

**🛡️ Smart Tourist Safety System** - Protecting tourists through intelligent monitoring and rapid response coordination.

*Built with ❤️ for emergency operations teams and tourism safety professionals.*
