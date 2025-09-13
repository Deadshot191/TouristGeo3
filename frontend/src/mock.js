// Mock data for Tourism Safety Dashboard

export const mockTourists = [
  {
    id: "TST-001",
    name: "John Smith",
    nationality: "USA",
    photo: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face",
    digitalId: "DIG-001-USA",
    status: "safe",
    safetyScore: 95,
    location: {
      lat: 27.0360,
      lng: 88.2627,
      address: "Mall Road, Darjeeling",
      timestamp: "2025-01-09T10:30:00Z"
    },
    itinerary: "Kolkata -> Darjeeling -> Gangtok",
    visitStartDate: "2025-01-08",
    visitEndDate: "2025-01-15",
    emergencyContacts: [
      { name: "Sarah Smith", phone: "+1-555-0123" },
      { name: "Embassy USA", phone: "+91-33-2419-8000" }
    ],
    alertHistory: [
      {
        id: "ALT-001",
        type: "route_deviation",
        location: "Tiger Hill Road",
        timestamp: "2025-01-08T14:20:00Z",
        status: "resolved"
      }
    ]
  },
  {
    id: "TST-002",
    name: "Maria Garcia",
    nationality: "Spain",
    photo: "https://images.unsplash.com/photo-1494790108755-2616b612b5e5?w=150&h=150&fit=crop&crop=face",
    digitalId: "DIG-002-ESP",
    status: "anomaly",
    safetyScore: 72,
    location: {
      lat: 27.0410,
      lng: 88.2690,
      address: "Chowrasta Mall, Darjeeling",
      timestamp: "2025-01-09T10:25:00Z"
    },
    itinerary: "Delhi -> Darjeeling -> Sikkim",
    visitStartDate: "2025-01-07",
    visitEndDate: "2025-01-20",
    emergencyContacts: [
      { name: "Pedro Garcia", phone: "+34-600-123456" },
      { name: "Embassy Spain", phone: "+91-11-4127-9000" }
    ],
    alertHistory: [
      {
        id: "ALT-002",
        type: "prolonged_inactivity",
        location: "Batasia Loop",
        timestamp: "2025-01-09T09:45:00Z",
        status: "in_progress"
      }
    ]
  },
  {
    id: "TST-003",
    name: "Hiroshi Tanaka",
    nationality: "Japan",
    photo: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face",
    digitalId: "DIG-003-JPN",
    status: "panic",
    safetyScore: 25,
    location: {
      lat: 27.0500,
      lng: 88.2800,
      address: "Happy Valley Tea Estate",
      timestamp: "2025-01-09T10:15:00Z"
    },
    itinerary: "Mumbai -> Darjeeling -> Kalimpong",
    visitStartDate: "2025-01-09",
    visitEndDate: "2025-01-18",
    emergencyContacts: [
      { name: "Yuki Tanaka", phone: "+81-90-1234-5678" },
      { name: "Embassy Japan", phone: "+91-11-2687-6581" }
    ],
    alertHistory: [
      {
        id: "ALT-003",
        type: "panic_button",
        location: "Happy Valley Tea Estate",
        timestamp: "2025-01-09T10:15:00Z",
        status: "new"
      }
    ]
  }
];

export const mockAlerts = [
  {
    id: "PN-9812",
    touristName: "Hiroshi Tanaka",
    touristId: "TST-003",
    type: "panic_button",
    location: "Happy Valley Tea Estate",
    timestamp: "2025-01-09T10:15:00Z",
    status: "new"
  },
  {
    id: "PN-9811",
    touristName: "Maria Garcia",
    touristId: "TST-002",
    type: "prolonged_inactivity",
    location: "Batasia Loop",
    timestamp: "2025-01-09T09:45:00Z",
    status: "in_progress"
  },
  {
    id: "PN-9810",
    touristName: "John Smith",
    touristId: "TST-001",
    type: "route_deviation",
    location: "Tiger Hill Road",
    timestamp: "2025-01-08T14:20:00Z",
    status: "resolved"
  },
  {
    id: "PN-9809",
    touristName: "Emma Wilson",
    touristId: "TST-004",
    type: "geofence_breach",
    location: "Restricted Military Zone",
    timestamp: "2025-01-08T11:30:00Z",
    status: "resolved"
  },
  {
    id: "PN-9808",
    touristName: "David Brown",
    touristId: "TST-005",
    type: "panic_button",
    location: "Ghum Railway Station",
    timestamp: "2025-01-08T08:45:00Z",
    status: "resolved"
  }
];

export const mockKPIs = {
  totalActiveTourists: 1482,
  activeAlerts: 5,
  safeStatus: 1477
};

export const mockOfficer = {
  name: "Inspector Raj Kumar",
  department: "Tourism Police",
  badge: "TP-001",
  avatar: "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=100&h=100&fit=crop&crop=face"
};

export const mockGeoFences = [
  {
    id: "GF-001",
    name: "Military Restricted Zone",
    type: "restricted",
    coordinates: [
      [27.0450, 88.2750],
      [27.0480, 88.2750],
      [27.0480, 88.2850],
      [27.0450, 88.2850]
    ]
  },
  {
    id: "GF-002",
    name: "Landslide Prone Area",
    type: "high_risk",
    coordinates: [
      [27.0300, 88.2500],
      [27.0350, 88.2500],
      [27.0350, 88.2600],
      [27.0300, 88.2600]
    ]
  }
];