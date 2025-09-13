# Tourism Safety Backend API Contracts

## Overview
Comprehensive FastAPI backend supporting real-time tourist monitoring, alerts, geo-fencing, AI anomaly detection, and secure authentication.

## Database Collections (MongoDB)

### 1. users (Officials)
```json
{
  "_id": "ObjectId",
  "email": "string",
  "password_hash": "string",
  "full_name": "string",
  "role": "police | tourism_admin",
  "department": "string",
  "badge_number": "string",
  "created_at": "datetime",
  "last_login": "datetime"
}
```

### 2. tourists
```json
{
  "_id": "ObjectId",
  "digital_id": "string (unique)",
  "full_name": "string",
  "nationality": "string",
  "photo_url": "string",
  "kyc_type": "passport | aadhaar",
  "kyc_id_hash": "string",
  "visit_start_date": "date",
  "visit_end_date": "date",
  "itinerary": "string",
  "emergency_contacts": [
    {
      "name": "string",
      "phone": "string",
      "relationship": "string"
    }
  ],
  "status": "safe | anomaly | panic",
  "safety_score": "number (0-100)",
  "created_at": "datetime",
  "last_location_update": "datetime"
}
```

### 3. location_history
```json
{
  "_id": "ObjectId",
  "tourist_id": "ObjectId",
  "coordinates": {
    "type": "Point",
    "coordinates": [longitude, latitude]
  },
  "address": "string",
  "timestamp": "datetime",
  "accuracy": "number",
  "speed": "number"
}
```

### 4. geofences
```json
{
  "_id": "ObjectId",
  "name": "string",
  "type": "restricted | high_risk | safe_zone",
  "risk_level": "low | medium | high | critical",
  "coordinates": {
    "type": "Polygon",
    "coordinates": [[[longitude, latitude]]]
  },
  "description": "string",
  "created_at": "datetime",
  "active": "boolean"
}
```

### 5. alerts
```json
{
  "_id": "ObjectId",
  "alert_id": "string (PN-XXXX)",
  "tourist_id": "ObjectId",
  "alert_type": "panic_button | geofence_breach | route_deviation | prolonged_inactivity",
  "severity": "low | medium | high | critical",
  "status": "new | in_progress | resolved",
  "location": {
    "coordinates": [longitude, latitude],
    "address": "string"
  },
  "description": "string",
  "created_at": "datetime",
  "resolved_at": "datetime",
  "resolved_by": "ObjectId (user_id)",
  "response_actions": ["string"]
}
```

## API Endpoints

### Authentication Service
- `POST /api/auth/login` - Officer login
- `GET /api/auth/me` - Get current user profile
- `POST /api/auth/refresh` - Refresh JWT token

### Tourist Management
- `GET /api/tourists` - List all tourists with filters
- `GET /api/tourists/{tourist_id}` - Get specific tourist details
- `PUT /api/tourists/{tourist_id}/status` - Update tourist status
- `GET /api/tourists/{tourist_id}/location-history` - Get location trail

### Location Tracking (WebSocket + REST)
- `WS /api/ws/location` - Real-time location updates
- `POST /api/location/update` - Manual location update
- `GET /api/location/live` - Get current locations of all tourists

### Alerts Management
- `GET /api/alerts` - List alerts with filters
- `POST /api/alerts/panic` - Create panic alert
- `PUT /api/alerts/{alert_id}/status` - Update alert status
- `POST /api/alerts/{alert_id}/actions` - Log response actions

### Geo-fencing
- `GET /api/geofences` - List all geo-fences
- `POST /api/geofences` - Create geo-fence
- `PUT /api/geofences/{fence_id}` - Update geo-fence
- `GET /api/geofences/check` - Check if coordinates are in restricted zone

### AI & Analytics
- `GET /api/analytics/dashboard` - Dashboard KPIs
- `POST /api/ai/analyze-route` - Analyze route deviation
- `GET /api/ai/safety-score/{tourist_id}` - Get safety score

### Real-time Features (WebSocket)
- Location updates broadcasting
- Alert notifications
- Status changes
- Dashboard live updates

## Frontend Integration Plan

### Mock Data Replacement
1. **Live Map Page**:
   - Replace `mockTourists` with `/api/tourists` API
   - Replace `mockKPIs` with `/api/analytics/dashboard`
   - Connect to WebSocket for real-time updates

2. **Alerts Page**:
   - Replace `mockAlerts` with `/api/alerts` API
   - Add real filtering with backend support
   - Real-time alert notifications

3. **Tourist Database**:
   - Connect to `/api/tourists` with filtering
   - Real tourist data with photos and details

4. **Tourist Detail Modal**:
   - Fetch from `/api/tourists/{id}` 
   - Get location history from `/api/tourists/{id}/location-history`
   - Connect action buttons to real endpoints

## AI/ML Features Implementation

### 1. Route Deviation Detection
- Compare current location trail with planned itinerary
- Alert if deviation > threshold distance/time

### 2. Prolonged Inactivity Detection  
- Monitor location updates frequency
- Alert if no movement for > configurable time

### 3. Safety Score Calculation
- Factors: current location risk, time of day, recent alerts, location history
- Real-time calculation and updates

### 4. Predictive Analytics
- Risk assessment based on historical data
- Zone popularity and safety trends

## Security Implementation
- JWT authentication for all endpoints
- Role-based access control (RBAC)
- Rate limiting for critical endpoints
- Input validation and sanitization
- Encrypted sensitive data storage

## Real-time Architecture
- WebSocket connections for live updates
- Background tasks for AI processing
- Async alert processing
- Event-driven location processing