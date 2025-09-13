import React from 'react';
import { X, MapPin, Phone, Calendar, AlertTriangle, Activity, Shield, FileText, PhoneCall, Truck, Users as UsersIcon } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Avatar, AvatarImage, AvatarFallback } from './ui/avatar';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Progress } from './ui/progress';
import { mockTourists } from '../mock';

const TouristDetailModal = ({ tourist, isOpen, onClose }) => {
  // Find full tourist data from mock (in real app, this would be an API call)
  const fullTourist = mockTourists.find(t => t.id === tourist.id) || tourist;

  const getStatusColor = (status) => {
    switch (status) {
      case 'safe': return 'bg-green-100 text-green-800 border-green-200';
      case 'anomaly': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'panic': return 'bg-red-100 text-red-800 border-red-200';
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
    if (score >= 80) return 'text-green-500';
    if (score >= 50) return 'text-yellow-500';
    return 'text-red-500';
  };

  if (!fullTourist) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto bg-slate-800 border-slate-700 text-white">
        <DialogHeader>
          <DialogTitle className="text-xl font-bold text-white">
            Detailed Tourist Report
          </DialogTitle>
        </DialogHeader>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
          {/* Left Column - Identity & Itinerary */}
          <div className="space-y-4">
            <Card className="bg-slate-700 border-slate-600">
              <CardHeader>
                <CardTitle className="text-lg text-white">Tourist Identity</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center space-x-4">
                  <Avatar className="w-16 h-16">
                    <AvatarImage src={fullTourist.photo} alt={fullTourist.name} />
                    <AvatarFallback className="bg-blue-600 text-white text-lg">
                      {fullTourist.name.split(' ').map(n => n[0]).join('')}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <h3 className="text-lg font-semibold text-white">{fullTourist.name}</h3>
                    <p className="text-slate-300">{fullTourist.nationality}</p>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-slate-400">Digital ID:</span>
                    <span className="text-sm text-white font-mono">{fullTourist.digitalId}</span>
                  </div>
                  
                  {/* QR Code Placeholder */}
                  <div className="bg-white p-4 rounded-lg flex items-center justify-center">
                    <div className="w-24 h-24 bg-black flex items-center justify-center text-white text-xs">
                      QR CODE
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-slate-700 border-slate-600">
              <CardHeader>
                <CardTitle className="text-lg text-white flex items-center">
                  <Calendar className="w-5 h-5 mr-2" />
                  Trip Details
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <p className="text-sm text-slate-400 mb-1">Itinerary</p>
                  <p className="text-sm text-white">{fullTourist.itinerary}</p>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-slate-400">Start Date</p>
                    <p className="text-sm text-white">{new Date(fullTourist.visitStartDate).toLocaleDateString()}</p>
                  </div>
                  <div>
                    <p className="text-sm text-slate-400">End Date</p>
                    <p className="text-sm text-white">{new Date(fullTourist.visitEndDate).toLocaleDateString()}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-slate-700 border-slate-600">
              <CardHeader>
                <CardTitle className="text-lg text-white flex items-center">
                  <Phone className="w-5 h-5 mr-2" />
                  Emergency Contacts
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {fullTourist.emergencyContacts?.map((contact, index) => (
                  <div key={index} className="flex justify-between items-center">
                    <div>
                      <p className="text-sm text-white font-medium">{contact.name}</p>
                      <p className="text-xs text-slate-400">{contact.phone}</p>
                    </div>
                    <Button size="sm" variant="outline" className="border-slate-600 text-slate-300 hover:bg-slate-600">
                      <PhoneCall className="w-4 h-4" />
                    </Button>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Middle Column - Live Status & History */}
          <div className="space-y-4">
            <Card className="bg-slate-700 border-slate-600">
              <CardHeader>
                <CardTitle className="text-lg text-white flex items-center">
                  <Activity className="w-5 h-5 mr-2" />
                  Live Status
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="text-center">
                  <Badge className={`text-lg px-4 py-2 ${getStatusColor(fullTourist.status)}`}>
                    {fullTourist.status?.toUpperCase() || 'UNKNOWN'}
                  </Badge>
                </div>

                <div className="space-y-3">
                  <div className="text-center">
                    <p className="text-sm text-slate-400 mb-2">Current Safety Score</p>
                    <div className="relative w-24 h-24 mx-auto">
                      <div className="w-24 h-24 rounded-full border-8 border-slate-600 flex items-center justify-center relative">
                        <span className={`text-2xl font-bold ${getSafetyScoreColor(fullTourist.safetyScore || 0)}`}>
                          {fullTourist.safetyScore || 0}
                        </span>
                        <span className="text-xs text-slate-400 absolute bottom-6">/100</span>
                      </div>
                    </div>
                  </div>

                  <div>
                    <p className="text-sm text-slate-400 mb-1">Last Known Location</p>
                    <div className="flex items-start space-x-2">
                      <MapPin className="w-4 h-4 mt-0.5 text-slate-400" />
                      <div>
                        <p className="text-sm text-white">{fullTourist.location?.address}</p>
                        <p className="text-xs text-slate-500">
                          {fullTourist.location?.timestamp && new Date(fullTourist.location.timestamp).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-slate-700 border-slate-600">
              <CardHeader>
                <CardTitle className="text-lg text-white flex items-center">
                  <AlertTriangle className="w-5 h-5 mr-2" />
                  Alert History
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 max-h-48 overflow-y-auto">
                  {fullTourist.alertHistory?.length > 0 ? (
                    fullTourist.alertHistory.map((alert, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-slate-800 rounded-lg">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-1">
                            <Badge className={getAlertTypeColor(alert.type)}>
                              {formatAlertType(alert.type)}
                            </Badge>
                            <Badge className={getStatusColor(alert.status)}>
                              {alert.status}
                            </Badge>
                          </div>
                          <p className="text-xs text-slate-400">{alert.location}</p>
                          <p className="text-xs text-slate-500">
                            {new Date(alert.timestamp).toLocaleString()}
                          </p>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-slate-400">No alerts recorded</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Map & Actions */}
          <div className="space-y-4">
            <Card className="bg-slate-700 border-slate-600">
              <CardHeader>
                <CardTitle className="text-lg text-white flex items-center">
                  <MapPin className="w-5 h-5 mr-2" />
                  Location History
                </CardTitle>
              </CardHeader>
              <CardContent>
                {/* Simulated Mini Map */}
                <div className="h-48 bg-slate-600 rounded-lg relative overflow-hidden">
                  <div className="absolute inset-0 opacity-20">
                    <div className="w-full h-full" style={{
                      backgroundImage: 'radial-gradient(circle at 1px 1px, rgba(255,255,255,0.15) 1px, transparent 0)',
                      backgroundSize: '10px 10px'
                    }}></div>
                  </div>
                  
                  {/* Location Trail */}
                  <div className="absolute inset-4">
                    <div className="w-full h-full relative">
                      {/* Trail points */}
                      {[...Array(5)].map((_, i) => (
                        <div
                          key={i}
                          className={`absolute w-3 h-3 rounded-full ${
                            i === 4 ? 'bg-red-500 animate-pulse' : 'bg-blue-400'
                          }`}
                          style={{
                            left: `${20 + i * 15}%`,
                            top: `${30 + Math.sin(i) * 20}%`
                          }}
                        />
                      ))}
                      
                      {/* Trail line */}
                      <svg className="absolute inset-0 w-full h-full">
                        <path
                          d="M20,40 Q35,20 50,45 Q65,60 80,50 Q95,30 110,35"
                          stroke="#60a5fa"
                          strokeWidth="2"
                          fill="none"
                          strokeDasharray="4,4"
                        />
                      </svg>
                    </div>
                  </div>
                  
                  <div className="absolute bottom-2 left-2 text-xs text-slate-300">
                    Recent Movement Trail
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-slate-700 border-slate-600">
              <CardHeader>
                <CardTitle className="text-lg text-white flex items-center">
                  <Shield className="w-5 h-5 mr-2" />
                  Response Actions
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button className="w-full bg-blue-600 hover:bg-blue-700 text-white" size="sm">
                  <Truck className="w-4 h-4 mr-2" />
                  Dispatch Nearest Unit
                </Button>
                
                <Button className="w-full bg-red-600 hover:bg-red-700 text-white" size="sm">
                  <PhoneCall className="w-4 h-4 mr-2" />
                  Contact Emergency Services
                </Button>
                
                <Button className="w-full bg-green-600 hover:bg-green-700 text-white" size="sm">
                  <Shield className="w-4 h-4 mr-2" />
                  Mark as Resolved
                </Button>
                
                <Button className="w-full bg-amber-600 hover:bg-amber-700 text-white" size="sm">
                  <FileText className="w-4 h-4 mr-2" />
                  Generate E-FIR
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default TouristDetailModal;