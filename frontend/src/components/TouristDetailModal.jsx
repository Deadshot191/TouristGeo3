import React from 'react';
import { X, MapPin, Phone, Calendar, AlertTriangle, Activity, Shield, FileText, PhoneCall, Truck, Users as UsersIcon, Clock, Globe, CreditCard } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Avatar, AvatarImage, AvatarFallback } from './ui/avatar';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Progress } from './ui/progress';
import { mockTourists } from '../mock';
import MiniMap from './MiniMap';

const TouristDetailModal = ({ tourist, isOpen, onClose }) => {
  // Find full tourist data from mock (in real app, this would be an API call)
  const fullTourist = mockTourists.find(t => t.id === tourist.id) || tourist;

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

  const isDataLocked = fullTourist.status === 'safe' && fullTourist.name === 'John Doe';

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

        <div className="grid grid-cols-12 gap-6 mt-6">
          {/* Left Column - Identity & Personal Info */}
          <div className="col-span-12 lg:col-span-4 space-y-6">
            <Card className="command-card">
              <CardHeader className="command-card-header">
                <CardTitle className="modal-section-title">
                  <CreditCard className="w-5 h-5" />
                  Tourist Identity
                </CardTitle>
              </CardHeader>
              <CardContent className="command-card-content space-y-4">
                <div className="flex items-center space-x-4">
                  <Avatar className="w-20 h-20 ring-4 ring-slate-600">
                    <AvatarImage src={fullTourist.photo} alt={fullTourist.name} />
                    <AvatarFallback className="bg-blue-600 text-white text-xl font-bold">
                      {fullTourist.name.split(' ').map(n => n[0]).join('')}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-white mb-1">{fullTourist.name}</h3>
                    <div className="flex items-center space-x-2 mb-2">
                      <Globe className="w-4 h-4 text-slate-400" />
                      <span className="text-slate-300">{fullTourist.nationality}</span>
                    </div>
                    <p className="text-sm text-slate-400 font-mono bg-slate-700 px-2 py-1 rounded">
                      {fullTourist.digitalId}
                    </p>
                  </div>
                </div>

                {/* QR Code and Verification */}
                <div className="flex items-center justify-center p-4 bg-white rounded-lg">
                  <div className="w-28 h-28 bg-black flex items-center justify-center text-white text-xs font-mono border-4 border-slate-300">
                    QR IDENTITY<br/>VERIFIED
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="command-card">
              <CardHeader className="command-card-header">
                <CardTitle className="modal-section-title">
                  <Calendar className="w-5 h-5" />
                  Trip Information
                </CardTitle>
              </CardHeader>
              <CardContent className="command-card-content space-y-4">
                <div>
                  <p className="text-sm font-medium text-slate-400 mb-2">Planned Itinerary</p>
                  <p className="text-sm text-white bg-slate-700 p-3 rounded-lg">{fullTourist.itinerary}</p>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-slate-700 p-3 rounded-lg">
                    <p className="text-xs text-slate-400 mb-1">Start Date</p>
                    <p className="text-sm font-semibold text-white">{new Date(fullTourist.visitStartDate).toLocaleDateString()}</p>
                  </div>
                  <div className="bg-slate-700 p-3 rounded-lg">
                    <p className="text-xs text-slate-400 mb-1">End Date</p>
                    <p className="text-sm font-semibold text-white">{new Date(fullTourist.visitEndDate).toLocaleDateString()}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="command-card">
              <CardHeader className="command-card-header">
                <CardTitle className="modal-section-title">
                  <Phone className="w-5 h-5" />
                  Emergency Contacts
                </CardTitle>
              </CardHeader>
              <CardContent className="command-card-content space-y-3">
                {isDataLocked ? (
                  <div className="text-center py-6">
                    <Shield className="w-12 h-12 text-slate-500 mx-auto mb-3" />
                    <p className="text-slate-400 text-sm">[DATA LOCKED - No Active Alert]</p>
                    <p className="text-slate-500 text-xs mt-1">Contact information protected</p>
                  </div>
                ) : (
                  fullTourist.emergencyContacts?.map((contact, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-slate-700 rounded-lg">
                      <div className="flex-1">
                        <p className="text-sm font-semibold text-white">{contact.name}</p>
                        <p className="text-xs text-slate-400">{contact.relationship}</p>
                        <p className="text-xs text-slate-300 font-mono">{contact.phone}</p>
                      </div>
                      <Button size="sm" className="action-btn-success">
                        <PhoneCall className="w-4 h-4" />
                      </Button>
                    </div>
                  ))
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
                        <span className={`text-3xl font-bold ${getSafetyScoreColor(fullTourist.safetyScore || 0)}`}>
                          {fullTourist.safetyScore || 0}
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
                  {fullTourist.alertHistory?.length > 0 ? (
                    fullTourist.alertHistory.map((alert, index) => (
                      <div key={index} className="p-3 bg-slate-700 rounded-lg border-l-4 border-amber-500">
                        <div className="flex items-center justify-between mb-2">
                          <Badge className={getAlertTypeColor(alert.type)}>
                            {formatAlertType(alert.type)}
                          </Badge>
                          <Badge className={getStatusColor(alert.status)}>
                            {alert.status}
                          </Badge>
                        </div>
                        <p className="text-xs text-slate-300 mb-1">{alert.location}</p>
                        <p className="text-xs text-slate-500">
                          {new Date(alert.timestamp).toLocaleString()}
                        </p>
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