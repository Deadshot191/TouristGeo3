// Mock data for Tourism Safety Dashboard - Demo Scenarios

export const mockTourists = [
  {
    id: "DIG-PANIC01",
    name: "Raj Verma",
    nationality: "India",
    photo: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face",
    digitalId: "DIG-PANIC01",
    status: "panic",
    safetyScore: 15,
    location: {
      lat: 27.0390,
      lng: 88.2640,
      address: "Mall Road, Darjeeling, West Bengal",
      timestamp: "2025-01-09T15:25:00Z"
    },
    itinerary: "Delhi -> Darjeeling -> Kalimpong",
    visitStartDate: "2025-01-10",
    visitEndDate: "2025-01-17",
    emergencyContacts: [
      { name: "Sunita Verma", phone: "+91-9876543210", relationship: "wife" },
      { name: "Dr. Amit Verma", phone: "+91-9876543211", relationship: "brother" },
      { name: "Delhi Police", phone: "+91-11-23454321", relationship: "emergency" }
    ],
    alertHistory: [
      {
        id: "PN-852E",
        type: "panic_button",
        location: "Mall Road, Darjeeling, West Bengal",
        timestamp: "2025-01-09T15:25:00Z",
        status: "new"
      }
    ]
  },
  {
    id: "DIG-BREACH02",
    name: "Emily Carter",
    nationality: "USA",
    photo: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face",
    digitalId: "DIG-BREACH02",
    status: "anomaly",
    safetyScore: 35,
    location: {
      lat: 27.0300,
      lng: 88.3000,
      address: "Restricted Forest Area, Darjeeling Hills",
      timestamp: "2025-01-09T15:18:00Z"
    },
    itinerary: "Kolkata -> Darjeeling -> Sikkim -> Gangtok",
    visitStartDate: "2025-01-08",
    visitEndDate: "2025-01-16",
    emergencyContacts: [
      { name: "Michael Carter", phone: "+1-555-0198", relationship: "husband" },
      { name: "Embassy USA", phone: "+91-33-2419-8000", relationship: "embassy" },
      { name: "Sarah Johnson", phone: "+1-555-0199", relationship: "sister" }
    ],
    alertHistory: [
      {
        id: "GB-F72F",
        type: "geofence_breach",
        location: "Restricted Forest Area, Darjeeling Hills",
        timestamp: "2025-01-09T15:18:00Z",
        status: "in_progress"
      }
    ]
  },
  {
    id: "DIG-DEVIATE03",
    name: "Priya Sharma",
    nationality: "India",
    photo: "https://images.unsplash.com/photo-1494790108755-2616b612b5e5?w=150&h=150&fit=crop&crop=face",
    digitalId: "DIG-DEVIATE03",
    status: "anomaly",
    safetyScore: 55,
    location: {
      lat: 27.0500,
      lng: 88.2950,
      address: "Tiger Hill Road, Darjeeling",
      timestamp: "2025-01-09T15:22:00Z"
    },
    itinerary: "Mumbai -> Darjeeling -> Kalimpong",
    visitStartDate: "2025-01-09",
    visitEndDate: "2025-01-14",
    emergencyContacts: [
      { name: "Rakesh Sharma", phone: "+91-9123456789", relationship: "father" },
      { name: "Meera Sharma", phone: "+91-9123456790", relationship: "mother" },
      { name: "Mumbai Police", phone: "+91-22-22621855", relationship: "emergency" }
    ],
    alertHistory: [
      {
        id: "RD-F9B4",
        type: "route_deviation",
        location: "Tiger Hill Road, Darjeeling",
        timestamp: "2025-01-09T15:22:00Z",
        status: "new"
      }
    ]
  },
  {
    id: "DIG-SAFE04",
    name: "John Doe",
    nationality: "UK",
    photo: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face",
    digitalId: "DIG-SAFE04",
    status: "safe",
    safetyScore: 95,
    location: {
      lat: 27.0395,
      lng: 88.2650,
      address: "The Mall, Darjeeling, West Bengal",
      timestamp: "2025-01-09T15:15:00Z"
    },
    itinerary: "London -> Kolkata -> Darjeeling -> Gangtok",
    visitStartDate: "2025-01-07",
    visitEndDate: "2025-01-19",
    emergencyContacts: [
      { name: "Jane Doe", phone: "+44-20-7946-0958", relationship: "wife" },
      { name: "British High Commission", phone: "+91-11-2419-2100", relationship: "embassy" }
    ],
    alertHistory: []
  },
  {
    id: "DIG-RESOLVED05",
    name: "Aisha Khan",
    nationality: "Bangladesh",
    photo: "https://images.unsplash.com/photo-1489424731084-a5d8b219a5bb?w=150&h=150&fit=crop&crop=face",
    digitalId: "DIG-RESOLVED05",
    status: "safe",
    safetyScore: 88,
    location: {
      lat: 27.0400,
      lng: 88.2655,
      address: "Hotel Mayfair, Darjeeling",
      timestamp: "2025-01-09T15:10:00Z"
    },
    itinerary: "Dhaka -> Kolkata -> Darjeeling -> Kalimpong",
    visitStartDate: "2025-01-06",
    visitEndDate: "2025-01-13",
    emergencyContacts: [
      { name: "Omar Khan", phone: "+880-1712345678", relationship: "brother" },
      { name: "Bangladesh High Commission", phone: "+91-11-2419-6389", relationship: "embassy" }
    ],
    alertHistory: [
      {
        id: "PI-2B85",
        type: "prolonged_inactivity",
        location: "Chowrasta, Darjeeling",
        timestamp: "2025-01-09T09:30:00Z",
        status: "resolved"
      }
    ]
  }
];

export const mockAlerts = [
  {
    id: "PN-852E",
    touristName: "Raj Verma",
    touristId: "DIG-PANIC01",
    type: "panic_button",
    severity: "critical",
    location: "Mall Road, Darjeeling, West Bengal",
    timestamp: "2025-01-09T15:25:00Z",
    status: "new",
    description: "Tourist activated panic button - immediate assistance required"
  },
  {
    id: "GB-F72F",
    touristName: "Emily Carter",
    touristId: "DIG-BREACH02",
    type: "geofence_breach",
    severity: "high",
    location: "Restricted Forest Area, Darjeeling Hills",
    timestamp: "2025-01-09T15:18:00Z",
    status: "in_progress",
    description: "Tourist entered restricted forest area - unauthorized access detected"
  },
  {
    id: "RD-F9B4",
    touristName: "Priya Sharma",
    touristId: "DIG-DEVIATE03",
    type: "route_deviation",
    severity: "medium",
    location: "Tiger Hill Road, Darjeeling",
    timestamp: "2025-01-09T15:22:00Z",
    status: "new",
    description: "Tourist deviated significantly from planned route - 3.2km off course"
  },
  {
    id: "PI-2B85",
    touristName: "Aisha Khan",
    touristId: "DIG-RESOLVED05",
    type: "prolonged_inactivity",
    severity: "medium",
    location: "Chowrasta, Darjeeling",
    timestamp: "2025-01-09T09:30:00Z",
    status: "resolved",
    description: "Tourist showed no movement for 2 hours - communication lost",
    resolvedAt: "2025-01-09T11:30:00Z"
  }
];

export const mockKPIs = {
  totalActiveTourists: 5,
  activeAlerts: 3,
  safeStatus: 2,
  highRiskTourists: 1,
  avgSafetyScore: 65.6
};

export const mockOfficer = {
  name: "Admin Priya Singh",
  department: "Tourism Department",
  badge: "TD-001",
  avatar: "https://images.unsplash.com/photo-1494790108755-2616b612b5e5?w=100&h=100&fit=crop&crop=face"
};

export const mockGeoFences = [
  {
    id: "GF-001",
    name: "Restricted Forest Area",
    type: "restricted",
    risk_level: "critical",
    coordinates: [
      [27.0200, 88.2900],
      [27.0400, 88.2900],
      [27.0400, 88.3100],
      [27.0200, 88.3100]
    ]
  },
  {
    id: "GF-002",
    name: "Military Restricted Zone",
    type: "restricted",
    risk_level: "critical",
    coordinates: [
      [27.0450, 88.2750],
      [27.0480, 88.2750],
      [27.0480, 88.2850],
      [27.0450, 88.2850]
    ]
  },
  {
    id: "GF-003",
    name: "Tourist Safe Zone - Mall Road",
    type: "safe_zone",
    risk_level: "low",
    coordinates: [
      [27.0380, 88.2600],
      [27.0420, 88.2600],
      [27.0420, 88.2700],
      [27.0380, 88.2700]
    ]
  }
];