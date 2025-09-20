import React, { useState, useEffect } from 'react';
import { MapPin, Users, AlertTriangle, Shield, Navigation } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { analyticsAPI, geofencesAPI, locationAPI, wsManager } from '../services/api';

// Coordinate Map Component for displaying tourist locations and geofences
const CoordinateMap = ({ tourists, geofences, onTouristClick, selectedTourist }) => {
  // Darjeeling area bounds (approximate)
  const MAP_BOUNDS = {
    minLat: 27.0,
    maxLat: 27.08,
    minLng: 88.2,
    maxLng: 88.35
  };

  // Convert lat/lng to pixel coordinates
  const coordToPixel = (lng, lat, mapWidth, mapHeight) => {
    const x = ((lng - MAP_BOUNDS.minLng) / (MAP_BOUNDS.maxLng - MAP_BOUNDS.minLng)) * mapWidth;
    const y = ((MAP_BOUNDS.maxLat - lat) / (MAP_BOUNDS.maxLat - MAP_BOUNDS.minLat)) * mapHeight;
    return { x: Math.max(0, Math.min(mapWidth, x)), y: Math.max(0, Math.min(mapHeight, y)) };
  };

  // Convert coordinates to SVG path for polygon
  const coordinatesToPath = (coordinates, mapWidth, mapHeight) => {
    if (!coordinates || !coordinates[0]) return '';
    
    const points = coordinates[0].map(coord => {
      const pixel = coordToPixel(coord[0], coord[1], mapWidth, mapHeight);
      return `${pixel.x},${pixel.y}`;
    });
    
    return `M ${points.join(' L ')} Z`;
  };

  const getGeofenceColor = (type, riskLevel) => {
    switch (type) {
      case 'restricted':
        return '#EF4444'; // Red for restricted areas
      case 'high_risk':
        return '#F59E0B'; // Amber for high risk
      case 'safe_zone':
        return '#22C55E'; // Green for safe zones
      default:
        return '#6B7280'; // Gray
    }
  };

  const getTouristColor = (status) => {
    switch (status) {
      case 'safe': return '#22C55E';
      case 'anomaly': return '#F59E0B';
      case 'panic': return '#EF4444';
      default: return '#6B7280';
    }
  };

  const mapWidth = 800;
  const mapHeight = 600;

  return (
    <div className="relative w-full h-full p-4">
      {/* Map Background */}
      <div className="relative w-full h-full rounded-lg overflow-hidden" style={{backgroundColor: '#0F172A'}}>
        {/* Grid Background */}
        <svg className="absolute inset-0 w-full h-full">
          <defs>
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1E293B" strokeWidth="1"/>
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />
        </svg>

        {/* Map Title */}
        <div className="absolute top-4 left-4 z-10">
          <div className="bg-gray-900 bg-opacity-90 rounded-lg px-3 py-2 border border-gray-700">
            <h3 className="text-white font-semibold text-sm">Darjeeling Tourism Safety Map</h3>
            <p className="text-gray-400 text-xs">
              {tourists.length} tourists • {geofences.length} geofences
            </p>
          </div>
        </div>

        {/* Coordinate Labels */}
        <div className="absolute top-4 right-4 z-10">
          <div className="bg-gray-900 bg-opacity-90 rounded-lg px-3 py-2 border border-gray-700">
            <p className="text-gray-400 text-xs">
              Bounds: {MAP_BOUNDS.minLat}°-{MAP_BOUNDS.maxLat}°N, {MAP_BOUNDS.minLng}°-{MAP_BOUNDS.maxLng}°E
            </p>
          </div>
        </div>

        {/* Geofences Layer */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none">
          {geofences.map((geofence, index) => {
            const color = getGeofenceColor(geofence.type, geofence.risk_level);
            const path = coordinatesToPath(geofence.coordinates?.coordinates, mapWidth, mapHeight);
            
            return (
              <g key={geofence.id || index}>
                <path
                  d={path}
                  fill={color}
                  fillOpacity="0.2"
                  stroke={color}
                  strokeWidth="2"
                  strokeDasharray={geofence.type === 'restricted' ? '5,5' : 'none'}
                />
              </g>
            );
          })}
        </svg>

        {/* Tourist Markers Layer */}
        {tourists.map((tourist, index) => {
          if (!tourist.coordinates || tourist.coordinates.length !== 2) return null;
          
          const pixel = coordToPixel(tourist.coordinates[0], tourist.coordinates[1], mapWidth, mapHeight);
          const color = getTouristColor(tourist.status);
          const isSelected = selectedTourist?.tourist_id === tourist.tourist_id;
          
          return (
            <div
              key={tourist.tourist_id || index}
              className="absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer z-20"
              style={{
                left: `${(pixel.x / mapWidth) * 100}%`,
                top: `${(pixel.y / mapHeight) * 100}%`,
              }}
              onClick={() => onTouristClick(tourist)}
            >
              {/* Tourist Marker */}
              <div className="relative">
                <div
                  className={`w-4 h-4 rounded-full border-2 border-white shadow-lg transition-all duration-200 ${
                    isSelected ? 'w-6 h-6 scale-125' : 'hover:scale-110'
                  }`}
                  style={{ backgroundColor: color }}
                />
                
                {/* Pulsing animation for panic status */}
                {tourist.status === 'panic' && (
                  <div
                    className="absolute inset-0 rounded-full animate-ping"
                    style={{ backgroundColor: color, opacity: 0.4 }}
                  />
                )}
                
                {/* Tourist Info Tooltip */}
                <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2 hidden hover:block">
                  <div className="bg-gray-900 bg-opacity-95 text-white px-3 py-2 rounded-lg text-xs whitespace-nowrap border border-gray-700 shadow-lg">
                    <div className="font-semibold">{tourist.tourist_name}</div>
                    <div className="text-gray-300">{tourist.digital_id}</div>
                    <div className="text-gray-400">Status: {tourist.status}</div>
                    <div className="text-gray-400">Score: {tourist.safety_score}</div>
                    {tourist.address && (
                      <div className="text-gray-400 max-w-48 truncate">{tourist.address}</div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          );
        })}

        {/* Legend */}
        <div className="absolute bottom-4 left-4 z-10">
          <div className="bg-gray-900 bg-opacity-90 rounded-lg p-3 border border-gray-700 max-w-64">
            <h4 className="text-white font-semibold text-sm mb-2">Legend</h4>
            
            {/* Tourist Status Legend */}
            <div className="mb-3">
              <p className="text-gray-300 text-xs mb-1">Tourist Status:</p>
              <div className="flex flex-wrap gap-2">
                <div className="flex items-center">
                  <div className="w-3 h-3 rounded-full bg-green-500 mr-1"></div>
                  <span className="text-xs text-gray-400">Safe</span>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 rounded-full bg-yellow-500 mr-1"></div>
                  <span className="text-xs text-gray-400">Anomaly</span>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 rounded-full bg-red-500 mr-1"></div>
                  <span className="text-xs text-gray-400">Panic</span>
                </div>
              </div>
            </div>

            {/* Geofence Legend */}
            <div>
              <p className="text-gray-300 text-xs mb-1">Geofences:</p>
              <div className="space-y-1">
                <div className="flex items-center">
                  <div className="w-3 h-1 bg-red-500 mr-2" style={{borderStyle: 'dashed'}}></div>
                  <span className="text-xs text-gray-400">Restricted</span>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-1 bg-yellow-500 mr-2"></div>
                  <span className="text-xs text-gray-400">High Risk</span>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-1 bg-green-500 mr-2"></div>
                  <span className="text-xs text-gray-400">Safe Zone</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Selected Tourist Info Panel */}
        {selectedTourist && (
          <div className="absolute top-4 right-4 z-30 w-80">
            <Card style={{backgroundColor: '#1F2937', borderColor: '#374151'}} className="border-2 border-blue-500">
              <CardHeader className="pb-3">
                <CardTitle style={{color: '#F3F4F6'}} className="flex items-center justify-between">
                  <span>{selectedTourist.tourist_name}</span>
                  <div 
                    className="px-2 py-1 text-xs font-bold rounded"
                    style={{
                      backgroundColor: getTouristColor(selectedTourist.status),
                      color: '#FFFFFF'
                    }}
                  >
                    {selectedTourist.status?.toUpperCase()}
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <p className="text-xs font-medium" style={{color: '#9CA3AF'}}>Digital ID</p>
                  <p style={{color: '#F3F4F6'}}>{selectedTourist.digital_id}</p>
                </div>
                <div>
                  <p className="text-xs font-medium" style={{color: '#9CA3AF'}}>Safety Score</p>
                  <p style={{color: '#F3F4F6'}}>{selectedTourist.safety_score}/100</p>
                </div>
                <div>
                  <p className="text-xs font-medium" style={{color: '#9CA3AF'}}>Location</p>
                  <p style={{color: '#F3F4F6'}} className="text-sm">
                    {selectedTourist.address || 'Location updating...'}
                  </p>
                  <p className="text-xs" style={{color: '#9CA3AF'}}>
                    {selectedTourist.coordinates?.[1]?.toFixed(4)}°N, {selectedTourist.coordinates?.[0]?.toFixed(4)}°E
                  </p>
                </div>
                {selectedTourist.timestamp && (
                  <div>
                    <p className="text-xs font-medium" style={{color: '#9CA3AF'}}>Last Update</p>
                    <p style={{color: '#F3F4F6'}} className="text-sm">
                      {new Date(selectedTourist.timestamp).toLocaleString()}
                    </p>
                  </div>
                )}
                <Button 
                  onClick={() => onTouristClick(null)} 
                  className="w-full mt-3"
                  variant="outline"
                >
                  Close Details
                </Button>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

const LiveMap = ({ onTouristSelect }) => {
  const [tourists, setTourists] = useState([]);
  const [kpis, setKpis] = useState({
    total_active_tourists: 0,
    active_alerts: 0,
    safe_status: 0,
    high_risk_tourists: 0
  });
  const [geofences, setGeofences] = useState([]);
  const [selectedTourist, setSelectedTourist] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load initial data
  useEffect(() => {
    loadDashboardData();
  }, []);

  // Set up real-time updates
  useEffect(() => {
    const handleLocationUpdate = (data) => {
      setTourists(prev => prev.map(tourist => 
        tourist.tourist_id === data.tourist_id 
          ? { ...tourist, ...data }
          : tourist
      ));
    };

    const handleStatusChange = (data) => {
      setTourists(prev => prev.map(tourist => 
        tourist.tourist_id === data.tourist_id 
          ? { ...tourist, status: data.new_status }
          : tourist
      ));
      // Refresh KPIs when status changes
      loadKPIs();
    };

    wsManager.subscribe('location_update', handleLocationUpdate);
    wsManager.subscribe('status_change', handleStatusChange);

    return () => {
      wsManager.unsubscribe('location_update', handleLocationUpdate);
      wsManager.unsubscribe('status_change', handleStatusChange);
    };
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        loadKPIs(),
        loadLiveLocations(),
        loadGeofences()
      ]);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const loadKPIs = async () => {
    try {
      const data = await analyticsAPI.getDashboardKPIs();
      setKpis(data);
    } catch (error) {
      console.error('Error loading KPIs:', error);
    }
  };

  const loadLiveLocations = async () => {
    try {
      const data = await locationAPI.getLiveLocations();
      setTourists(data);
    } catch (error) {
      console.error('Error loading live locations:', error);
    }
  };

  const loadGeofences = async () => {
    try {
      const data = await geofencesAPI.getGeofences();
      setGeofences(data);
    } catch (error) {
      console.error('Error loading geofences:', error);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'safe': return '#22C55E'; // Safe Green
      case 'anomaly': return '#F59E0B'; // Warning Amber
      case 'panic': return '#EF4444'; // Panic Red
      default: return '#6B7280'; // Gray
    }
  };

  const getStatusBadgeStyle = (status) => {
    const backgroundColor = getStatusColor(status);
    return {
      backgroundColor,
      color: '#FFFFFF',
      border: `2px solid ${backgroundColor}`,
      fontWeight: 'bold'
    };
  };

  const handleTouristClick = (tourist) => {
    setSelectedTourist(tourist);
    if (onTouristSelect) {
      onTouristSelect(tourist);
    }
  };

  const refreshData = () => {
    loadDashboardData();
  };

  if (loading && tourists.length === 0) {
    return (
      <div className="p-6 h-full flex items-center justify-center" style={{backgroundColor: '#111827'}}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 mx-auto mb-4" style={{borderColor: '#3B82F6'}}></div>
          <p style={{color: '#9CA3AF'}}>Loading live map data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 h-full flex items-center justify-center" style={{backgroundColor: '#111827'}}>
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 mx-auto mb-4" style={{color: '#EF4444'}} />
          <p style={{color: '#9CA3AF'}} className="mb-4">{error}</p>
          <Button onClick={refreshData} className="action-btn-primary">
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col" style={{backgroundColor: '#111827'}}>
      {/* Header Section with Enhanced KPI Cards */}
      <div className="flex-shrink-0 p-6 border-b" style={{borderColor: '#374151'}}>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold" style={{color: '#F3F4F6'}}>Live Map Dashboard</h1>
            <p style={{color: '#9CA3AF'}}>Real-time tourist location monitoring and emergency response</p>
          </div>
          <Button onClick={refreshData} className="action-btn-primary">
            <MapPin className="w-4 h-4 mr-2" />
            Refresh Data
          </Button>
        </div>

        {/* Enhanced KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className="min-w-[140px] border" style={{backgroundColor: '#1F2937', borderColor: '#374151'}}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-medium uppercase tracking-wide mb-1" style={{color: '#9CA3AF'}}>Total Active</p>
                  <p className="text-2xl font-bold leading-none" style={{color: '#3B82F6'}}>{kpis.total_active_tourists || tourists.length}</p>
                </div>
                <Users className="w-8 h-8" style={{color: '#3B82F6'}} />
              </div>
            </CardContent>
          </Card>

          <Card className="min-w-[140px] border" style={{backgroundColor: '#1F2937', borderColor: '#374151'}}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-medium uppercase tracking-wide mb-1" style={{color: '#9CA3AF'}}>Active Alerts</p>
                  <p className="text-2xl font-bold leading-none" style={{color: '#EF4444'}}>{kpis.active_alerts}</p>
                </div>
                <AlertTriangle className="w-8 h-8" style={{color: '#EF4444'}} />
              </div>
            </CardContent>
          </Card>

          <Card className="min-w-[140px] border" style={{backgroundColor: '#1F2937', borderColor: '#374151'}}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-medium uppercase tracking-wide mb-1" style={{color: '#9CA3AF'}}>Safe Status</p>
                  <p className="text-2xl font-bold leading-none" style={{color: '#22C55E'}}>{kpis.safe_status}</p>
                </div>
                <Shield className="w-8 h-8" style={{color: '#22C55E'}} />
              </div>
            </CardContent>
          </Card>

          <Card className="min-w-[140px] border" style={{backgroundColor: '#1F2937', borderColor: '#374151'}}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-medium uppercase tracking-wide mb-1" style={{color: '#9CA3AF'}}>High Risk</p>
                  <p className="text-2xl font-bold leading-none" style={{color: '#F59E0B'}}>{kpis.high_risk_tourists || 0}</p>
                </div>
                <AlertTriangle className="w-8 h-8" style={{color: '#F59E0B'}} />
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Main Map Container */}
      <div className="flex-1 relative">
        {/* Interactive Map with Tourist Locations and Geofences */}
        <div className="absolute inset-0 rounded-lg border m-4 overflow-hidden" style={{backgroundColor: '#1F2937', borderColor: '#374151'}}>
          <CoordinateMap 
            tourists={tourists} 
            geofences={geofences} 
            onTouristClick={handleTouristClick}
            selectedTourist={selectedTourist}
          />
        </div>

        {/* Tourist Markers Overlay - Now part of the map */}
      </div>
    </div>
  );
};

export default LiveMap;