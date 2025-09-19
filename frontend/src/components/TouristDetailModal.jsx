import React, { useState, useEffect } from 'react';
import { X, MapPin, Phone, Calendar, AlertTriangle, Activity, Shield, FileText, PhoneCall, Truck, Users as UsersIcon, Clock, Globe, CreditCard } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Avatar, AvatarImage, AvatarFallback } from './ui/avatar';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Progress } from './ui/progress';
import { touristsAPI } from '../services/api';
import MiniMap from './MiniMap';

const TouristDetailModal = ({ tourist, isOpen, onClose }) => {
  const [fullTourist, setFullTourist] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch full tourist data when modal opens
  useEffect(() => {
    if (isOpen && tourist?.id) {
      fetchTouristData();
    }
  }, [isOpen, tourist?.id]);

  const fetchTouristData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch tourist details and alerts in parallel
      const [touristData, alertsData] = await Promise.all([
        touristsAPI.getTourist(tourist.id),
        touristsAPI.getTouristAlerts(tourist.id, 50)
      ]);
      
      setFullTourist(touristData);
      setAlerts(alertsData);
    } catch (err) {
      console.error('Error fetching tourist data:', err);
      setError('Failed to load tourist data');
      // Fallback to passed tourist data
      setFullTourist(tourist);
      setAlerts([]);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'safe': return 'status-badge-safe';
      case 'anomaly': return 'status-badge-anomaly';
      case 'panic': return 'status-badge-panic';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getAlertTypeColor = (type) => {
    switch (type) {
      case 'panic_button': return 'bg-red-100 text-red-800 border-red-200';
      case 'geofence_breach': return 'bg-red-100 text-red-800 border-red-200';
      case 'route_deviation': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'prolonged_inactivity': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const formatAlertType = (type) => {
    return type.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  const getSafetyScoreColor = (score) => {
    if (score >= 80) return 'text-emerald-500';
    if (score >= 50) return 'text-amber-500';
    return 'text-red-500';
  };

  // Check if data should be locked (SAFE status tourists have sensitive data hidden)
  const isDataLocked = fullTourist?.status === 'safe';

  // Show loading state
  if (loading) {
    return (
      <Dialog open={isOpen} onOpenChange={onClose}>
        <DialogContent className="max-w-7xl max-h-[95vh] overflow-y-auto bg-slate-800 border-slate-700 text-white">
          <div className="flex items-center justify-center p-8">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
              <p className="text-slate-400">Loading tourist details...</p>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  // Show error state
  if (error) {
    return (
      <Dialog open={isOpen} onOpenChange={onClose}>
        <DialogContent className="max-w-7xl max-h-[95vh] overflow-y-auto bg-slate-800 border-slate-700 text-white">
          <div className="flex items-center justify-center p-8">
            <div className="text-center">
              <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
              <p className="text-slate-400">{error}</p>
              <Button onClick={fetchTouristData} className="mt-4">
                Try Again
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  if (!fullTourist) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-7xl max-h-[95vh] overflow-y-auto bg-slate-800 border-slate-700 text-white">
        <DialogHeader className="pb-6 border-b border-slate-700">
          <div className="flex items-center justify-between">
            <div>
              <DialogTitle className="page-title">
                Detailed Tourist Report
              </DialogTitle>
              <p className="text-slate-400 text-sm mt-1">
                Comprehensive overview and real-time monitoring data
              </p>
            </div>
            <div className="flex items-center space-x-3">
              <Badge className={`${getStatusColor(fullTourist.status)} px-4 py-2 text-sm`}>
                {fullTourist.status?.toUpperCase() || 'UNKNOWN'}
              </Badge>
            </div>
          </div>
        </DialogHeader>

        <div className="grid grid-cols-12 gap-8 mt-6">
          {/* Left Column - Identity & Profile */}
          <div className="col-span-12 lg:col-span-4 space-y-6">
            {/* Tourist Identity - Simplified and Clean */}
            <Card className="command-card border-2 border-slate-600">
              <CardHeader className="command-card-header pb-4">
                <CardTitle className="modal-section-title text-lg font-bold">
                  <CreditCard className="w-6 h-6" />
                  Tourist Identity
                </CardTitle>
              </CardHeader>
              <CardContent className="command-card-content space-y-5">
                <div className="flex items-center space-x-4">
                  <Avatar className="w-24 h-24 ring-4 ring-blue-500 ring-opacity-50">
                    <AvatarImage src={fullTourist.photo_url} alt={fullTourist.full_name} />
                    <AvatarFallback className="bg-blue-600 text-white text-2xl font-bold">
                      {fullTourist.full_name ? fullTourist.full_name.split(' ').map(n => n[0]).join('') : 'NA'}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1">
                    <h3 className="text-2xl font-bold text-white mb-2">{fullTourist.full_name || 'Unknown'}</h3>
                    <div className="flex items-center space-x-2 mb-3">
                      <Globe className="w-5 h-5 text-blue-400" />
                      <span className="text-lg text-slate-200 font-medium">{fullTourist.nationality || 'Unknown'}</span>
                    </div>
                  </div>
                </div>

                {/* Digital ID - More Prominent */}
                <div className="bg-gradient-to-r from-blue-900 to-blue-800 p-4 rounded-lg border border-blue-400">
                  <p className="text-xs text-blue-200 mb-1 uppercase tracking-wide">Digital ID</p>
                  <p className="text-lg font-mono font-bold text-white">{fullTourist.digital_id || 'N/A'}</p>
                </div>
              </CardContent>
            </Card>

            {/* Trip Information - Streamlined */}
            <Card className="command-card border-2 border-slate-600">
              <CardHeader className="command-card-header pb-4">
                <CardTitle className="modal-section-title text-lg font-bold">
                  <Calendar className="w-6 h-6" />
                  Planned Itinerary
                </CardTitle>
              </CardHeader>
              <CardContent className="command-card-content space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-slate-700 p-4 rounded-lg border border-slate-500">
                    <p className="text-xs text-slate-400 mb-1 uppercase tracking-wide">Start Date</p>
                    <p className="text-base font-bold text-white">{fullTourist.visit_start_date ? new Date(fullTourist.visit_start_date).toLocaleDateString() : 'N/A'}</p>
                  </div>
                  <div className="bg-slate-700 p-4 rounded-lg border border-slate-500">
                    <p className="text-xs text-slate-400 mb-1 uppercase tracking-wide">End Date</p>
                    <p className="text-base font-bold text-white">{fullTourist.visit_end_date ? new Date(fullTourist.visit_end_date).toLocaleDateString() : 'N/A'}</p>
                  </div>
                </div>
                <div className="bg-slate-700 p-4 rounded-lg border border-slate-500">
                  <p className="text-xs text-slate-400 mb-2 uppercase tracking-wide">Route Details</p>
                  <p className="text-sm text-white leading-relaxed">{fullTourist.itinerary || 'No itinerary available'}</p>
                </div>
              </CardContent>
            </Card>

            {/* Emergency Contacts - Operator Focused */}
            <Card className="command-card border-2 border-slate-600">
              <CardHeader className="command-card-header pb-4">
                <CardTitle className="modal-section-title text-lg font-bold">
                  <Phone className="w-6 h-6" />
                  Emergency Contacts
                </CardTitle>
              </CardHeader>
              <CardContent className="command-card-content space-y-3">
                {isDataLocked ? (
                  <div className="text-center py-8 bg-slate-700 rounded-lg border border-slate-500">
                    <Shield className="w-16 h-16 text-slate-500 mx-auto mb-4" />
                    <p className="text-slate-300 text-lg font-medium">[DATA LOCKED]</p>
                    <p className="text-slate-500 text-sm mt-1">Contact information protected</p>
                  </div>
                ) : (
                  fullTourist.emergency_contacts?.length > 0 ? (
                    fullTourist.emergency_contacts.map((contact, index) => (
                      <div key={index} className="bg-slate-700 p-4 rounded-lg border border-slate-500 hover:bg-slate-600 transition-colors">
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <p className="text-lg font-bold text-white mb-1">{contact.name}</p>
                            <p className="text-sm text-slate-400 mb-2">{contact.relationship}</p>
                            <p className="text-base font-mono text-blue-300 font-medium">{contact.phone}</p>
                          </div>
                          <Button size="lg" className="action-btn-success ml-4 px-4 py-2">
                            <PhoneCall className="w-5 h-5" />
                          </Button>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-6 bg-slate-700 rounded-lg border border-slate-500">
                      <p className="text-slate-400 text-base">No emergency contacts available</p>
                    </div>
                  )
                )}
              </CardContent>
            </Card>
          </div>

          {/* Middle Column - Live Status & Safety */}
          <div className="col-span-12 lg:col-span-4 space-y-6">
            <Card className="command-card">
              <CardHeader className="command-card-header">
                <CardTitle className="modal-section-title">
                  <Activity className="w-5 h-5" />
                  Live Safety Status
                </CardTitle>
              </CardHeader>
              <CardContent className="command-card-content space-y-6">
                {/* Safety Score Circle */}
                <div className="text-center">
                  <div className="relative w-32 h-32 mx-auto mb-4">
                    <div className="w-32 h-32 rounded-full border-8 border-slate-600 flex items-center justify-center relative bg-gradient-to-br from-slate-700 to-slate-800">
                      <div className="text-center">
                        <span className={`text-3xl font-bold ${getSafetyScoreColor(fullTourist.safety_score || 0)}`}>
                          {fullTourist.safety_score || 0}
                        </span>
                        <div className="text-xs text-slate-400">/100</div>
                      </div>
                    </div>
                    <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2">
                      <Badge className={getStatusColor(fullTourist.status)}>
                        {fullTourist.status?.toUpperCase()}
                      </Badge>
                    </div>
                  </div>
                </div>

                {/* Location Info */}
                <div className="space-y-3">
                  <div className="bg-slate-700 p-4 rounded-lg">
                    <div className="flex items-start space-x-3">
                      <MapPin className="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" />
                      <div className="flex-1">
                        <p className="text-sm font-medium text-white mb-1">Current Location</p>
                        <p className="text-sm text-slate-300">{fullTourist.location?.address || 'Location updating...'}</p>
                        <div className="flex items-center space-x-2 mt-2">
                          <Clock className="w-3 h-3 text-slate-400" />
                          <p className="text-xs text-slate-400">
                            Last update: {fullTourist.location?.timestamp ? new Date(fullTourist.location.timestamp).toLocaleString() : 'Unknown'}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="command-card">
              <CardHeader className="command-card-header">
                <CardTitle className="modal-section-title">
                  <AlertTriangle className="w-5 h-5" />
                  Alert History
                </CardTitle>
              </CardHeader>
              <CardContent className="command-card-content">
                <div className="space-y-3 max-h-64 overflow-y-auto">
                  {alerts?.length > 0 ? (
                    alerts.map((alert, index) => (
                      <div key={alert.id || index} className="p-3 bg-slate-700 rounded-lg border-l-4 border-amber-500">
                        <div className="flex items-center justify-between mb-2">
                          <Badge className={getAlertTypeColor(alert.alert_type)}>
                            {formatAlertType(alert.alert_type)}
                          </Badge>
                          <Badge className={`${alert.status === 'new' ? 'bg-red-100 text-red-800 border-red-200' : 
                                              alert.status === 'in_progress' ? 'bg-yellow-100 text-yellow-800 border-yellow-200' : 
                                              'bg-green-100 text-green-800 border-green-200'}`}>
                            {alert.status.replace('_', ' ').toUpperCase()}
                          </Badge>
                        </div>
                        <p className="text-xs text-slate-300 mb-1">{alert.location?.address || 'Location unknown'}</p>
                        <p className="text-xs text-slate-500">
                          {alert.created_at ? new Date(alert.created_at).toLocaleString() : 'Unknown time'}
                        </p>
                        {alert.description && (
                          <p className="text-xs text-slate-400 mt-1">{alert.description}</p>
                        )}
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-6">
                      <AlertTriangle className="w-8 h-8 text-slate-500 mx-auto mb-2" />
                      <p className="text-sm text-slate-400">No alerts recorded</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Map & Response Actions */}
          <div className="col-span-12 lg:col-span-4 space-y-6">
            <Card className="command-card">
              <CardHeader className="command-card-header">
                <CardTitle className="modal-section-title">
                  <MapPin className="w-5 h-5" />
                  Location History Trail
                </CardTitle>
              </CardHeader>
              <CardContent className="command-card-content">
                <MiniMap 
                  locationHistory={fullTourist.locationHistory}
                  currentLocation={fullTourist.location}
                  className="h-64"
                />
                <div className="mt-3 text-xs text-slate-400 text-center">
                  Interactive trail showing recent movement patterns
                </div>
              </CardContent>
            </Card>

            <Card className="command-card">
              <CardHeader className="command-card-header">
                <CardTitle className="modal-section-title">
                  <Shield className="w-5 h-5" />
                  Emergency Response
                </CardTitle>
              </CardHeader>
              <CardContent className="command-card-content">
                <div className="grid grid-cols-1 gap-3">
                  <Button className="action-btn-primary justify-center py-3">
                    <Truck className="w-4 h-4 mr-2" />
                    Dispatch Nearest Unit
                  </Button>
                  
                  <Button className="action-btn-danger justify-center py-3">
                    <PhoneCall className="w-4 h-4 mr-2" />
                    Emergency Services
                  </Button>
                  
                  <div className="grid grid-cols-2 gap-2">
                    <Button className="action-btn-success text-sm py-2">
                      <Shield className="w-4 h-4 mr-1" />
                      Mark Safe
                    </Button>
                    
                    <Button className="action-btn-warning text-sm py-2">
                      <FileText className="w-4 h-4 mr-1" />
                      E-FIR
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default TouristDetailModal;