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
      case 'safe': return '#2ecc71';
      case 'anomaly': return '#f39c12';
      case 'panic': return '#e74c3c';
      default: return '#95a5a6';
    }
  };

  const getStatusBadgeColor = (status) => {
    switch (status) {
      case 'safe': return 'bg-green-100 text-green-800 border-green-200';
      case 'anomaly': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'panic': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const handleMarkerClick = (tourist) => {
    setSelectedTourist(tourist);
  };

  return (
    <div className="h-full flex flex-col bg-slate-900">
      {/* Header Section */}
      <div className="p-6 border-b border-slate-700">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-white">Real-time Tourist Monitoring</h1>
          
          {/* KPI Cards */}
          <div className="flex space-x-4">
            <Card className="bg-slate-800 border-slate-700">
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <Users className="w-5 h-5 text-blue-400" />
                  <div>
                    <p className="text-xs text-slate-400">Total Active</p>
                    <p className="text-lg font-bold text-white">{mockKPIs.totalActiveTourists}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-slate-800 border-slate-700">
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <AlertTriangle className="w-5 h-5 text-red-400" />
                  <div>
                    <p className="text-xs text-slate-400">Active Alerts</p>
                    <p className="text-lg font-bold text-red-400">{mockKPIs.activeAlerts}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-slate-800 border-slate-700">
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <Shield className="w-5 h-5 text-green-400" />
                  <div>
                    <p className="text-xs text-slate-400">Safe Status</p>
                    <p className="text-lg font-bold text-green-400">{mockKPIs.safeStatus}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* Map Component */}
      <div className="flex-1 relative">
        {/* Simulated Map Container */}
        <div className="w-full h-full bg-slate-700 relative overflow-hidden">
          {/* Map Background Pattern */}
          <div className="absolute inset-0 opacity-10">
            <div className="w-full h-full" style={{
              backgroundImage: `radial-gradient(circle at 1px 1px, rgba(255,255,255,0.15) 1px, transparent 0)`,
              backgroundSize: '20px 20px'
            }}></div>
          </div>

          {/* Tourist Markers */}
          {tourists.map((tourist) => (
            <div
              key={tourist.id}
              className="absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer transition-all hover:scale-110"
              style={{
                left: `${30 + (Math.random() * 40)}%`,
                top: `${20 + (Math.random() * 60)}%`
              }}
              onClick={() => handleMarkerClick(tourist)}
            >
              <div 
                className="w-4 h-4 rounded-full border-2 border-white shadow-lg animate-pulse"
                style={{ backgroundColor: getStatusColor(tourist.status) }}
              />
              {tourist.status === 'panic' && (
                <div className="absolute -top-8 -left-8 w-16 h-16 border-2 border-red-500 rounded-full animate-ping opacity-75" />
              )}
            </div>
          ))}

          {/* Geo-fenced Zones */}
          {mockGeoFences.map((zone) => (
            <div
              key={zone.id}
              className="absolute bg-red-500 bg-opacity-20 border-2 border-red-500 border-dashed rounded-lg"
              style={{
                left: `${60 + (Math.random() * 20)}%`,
                top: `${30 + (Math.random() * 30)}%`,
                width: '120px',
                height: '80px'
              }}
            >
              <div className="absolute -top-6 left-0 text-xs text-red-400 font-medium bg-slate-800 px-2 py-1 rounded">
                {zone.name}
              </div>
            </div>
          ))}

          {/* Map Legend */}
          <div className="absolute bottom-4 left-4 bg-slate-800 border border-slate-600 rounded-lg p-4">
            <h3 className="text-sm font-medium text-white mb-2">Legend</h3>
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full bg-green-500"></div>
                <span className="text-xs text-slate-300">Safe</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                <span className="text-xs text-slate-300">Anomaly</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full bg-red-500"></div>
                <span className="text-xs text-slate-300">Panic Alert</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 border-2 border-red-500 border-dashed"></div>
                <span className="text-xs text-slate-300">Restricted Zone</span>
              </div>
            </div>
          </div>
        </div>

        {/* Tourist Info Panel */}
        {selectedTourist && (
          <div className="absolute top-4 right-4 w-80 bg-slate-800 border border-slate-600 rounded-lg shadow-xl">
            <div className="p-4">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <h3 className="font-medium text-white">{selectedTourist.name}</h3>
                  <p className="text-sm text-slate-400">{selectedTourist.digitalId}</p>
                </div>
                <Badge className={getStatusBadgeColor(selectedTourist.status)}>
                  {selectedTourist.status.toUpperCase()}
                </Badge>
              </div>
              
              <div className="space-y-2 mb-4">
                <div className="flex items-center space-x-2 text-sm">
                  <MapPin className="w-4 h-4 text-slate-400" />
                  <span className="text-slate-300">{selectedTourist.location.address}</span>
                </div>
                <p className="text-xs text-slate-500">
                  Last updated: {new Date(selectedTourist.location.timestamp).toLocaleTimeString()}
                </p>
              </div>

              <Button 
                onClick={() => onTouristSelect(selectedTourist)}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white"
              >
                View Details
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default LiveMap;