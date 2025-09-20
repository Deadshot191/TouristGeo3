import React, { useState, useEffect } from 'react';
import { MapPin, Users, AlertTriangle, Shield } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { analyticsAPI, geofencesAPI, locationAPI, wsManager } from '../services/api';

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
    onTouristSelect(tourist);
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

        {/* Tourist Markers Overlay (Mock) */}
        <div className="absolute top-8 right-8 w-80 max-h-96 overflow-y-auto">
          <Card style={{backgroundColor: '#1F2937', borderColor: '#374151'}}>
            <CardHeader>
              <CardTitle style={{color: '#F3F4F6'}}>Active Tourists</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {tourists.slice(0, 5).map((tourist, index) => (
                <div
                  key={tourist.tourist_id || index}
                  className="p-3 rounded-lg border cursor-pointer transition-colors"
                  style={{backgroundColor: '#374151', borderColor: '#4B5563'}}
                  onClick={() => handleTouristClick(tourist)}
                  onMouseEnter={(e) => {
                    e.target.style.backgroundColor = '#4B5563';
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.backgroundColor = '#374151';
                  }}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium" style={{color: '#F3F4F6'}}>
                      {tourist.tourist_name || 'Unknown'}
                    </span>
                    <div 
                      className="px-2 py-1 text-xs font-bold rounded"
                      style={getStatusBadgeStyle(tourist.status)}
                    >
                      {tourist.status?.toUpperCase() || 'UNKNOWN'}
                    </div>
                  </div>
                  <div className="flex items-center text-sm" style={{color: '#9CA3AF'}}>
                    <MapPin className="w-4 h-4 mr-1" />
                    <span className="truncate">
                      {tourist.address || 'Location updating...'}
                    </span>
                  </div>
                  {tourist.timestamp && (
                    <div className="text-xs mt-1" style={{color: '#9CA3AF'}}>
                      Last update: {new Date(tourist.timestamp).toLocaleTimeString()}
                    </div>
                  )}
                </div>
              ))}
              
              {tourists.length === 0 && (
                <div className="text-center py-4">
                  <p style={{color: '#9CA3AF'}}>No active tourists found</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default LiveMap;