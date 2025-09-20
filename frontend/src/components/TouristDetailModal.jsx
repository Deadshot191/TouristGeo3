import React, { useState, useEffect, useRef } from 'react';
import { X, MapPin, Phone, Calendar, AlertTriangle, Activity, Shield, FileText, PhoneCall, Truck, Users as UsersIcon, Clock, Globe, CreditCard, Download, Save, Printer, Signature, QrCode } from 'lucide-react';
import jsPDF from 'jspdf';
import QRCode from 'qrcode';
import SignaturePad from 'signature_pad';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Avatar, AvatarImage, AvatarFallback } from './ui/avatar';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Progress } from './ui/progress';
import { Input } from './ui/input'; 
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { touristsAPI } from '../services/api';
import MiniMap from './MiniMap';

const TouristDetailModal = ({ tourist, isOpen, onClose }) => {
  const [fullTourist, setFullTourist] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // E-FIR Modal State
  const [efirModalOpen, setEfirModalOpen] = useState(false);
  const [efirData, setEfirData] = useState({
    incidentType: '',
    incidentDescription: '',
    officerName: '',
    officerBadge: '',
    stationName: '',
    additionalDetails: '',
    witnesses: '',
    actionTaken: ''
  });

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
      case 'safe': return 'bg-opacity-100 shadow-lg animate-none';
      case 'anomaly': return 'bg-opacity-100 shadow-lg animate-pulse'; 
      case 'panic': return 'bg-opacity-100 shadow-lg animate-pulse';
      default: return 'bg-gray-600 text-white border-gray-400 shadow-lg';
    }
  };

  const getStatusBackgroundColor = (status) => {
    switch (status) {
      case 'safe': return '#22C55E'; // Safe Green
      case 'anomaly': return '#F59E0B'; // Warning Amber
      case 'panic': return '#EF4444'; // Panic Red
      default: return '#6B7280'; // Gray
    }
  };

  const getStatusBorderColor = (status) => {
    switch (status) {
      case 'safe': return '#16A34A';
      case 'anomaly': return '#D97706';
      case 'panic': return '#DC2626';
      default: return '#4B5563';
    }
  };

  const getAlertTypeColor = (type) => {
    switch (type) {
      case 'panic_button': return 'text-white border-red-500';
      case 'geofence_breach': return 'text-white border-red-500';
      case 'route_deviation': return 'text-white border-yellow-500';
      case 'prolonged_inactivity': return 'text-white border-yellow-500';
      default: return 'text-white border-gray-500';
    }
  };
  
  const getAlertTypeBackgroundColor = (type) => {
    switch (type) {
      case 'panic_button': return '#EF4444';
      case 'geofence_breach': return '#EF4444';
      case 'route_deviation': return '#F59E0B';
      case 'prolonged_inactivity': return '#F59E0B';
      default: return '#6B7280';
    }
  };

  const formatAlertType = (type) => {
    return type.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  const getSafetyScoreColor = (score) => {
    if (score >= 80) return '#22C55E'; // Safe Green
    if (score >= 50) return '#F59E0B'; // Warning Amber  
    return '#EF4444'; // Panic Red
  };

  // Check if data should be locked (SAFE status tourists have sensitive data hidden)
  const isDataLocked = fullTourist?.status === 'safe';

  // E-FIR Functions
  const handleCreateEFIR = () => {
    // Auto-populate E-FIR data based on tourist and alert information
    const activeAlert = alerts.find(alert => alert.status === 'new' || alert.status === 'in_progress');
    
    setEfirData({
      incidentType: activeAlert ? formatAlertType(activeAlert.alert_type) : 'General Emergency',
      incidentDescription: activeAlert ? 
        `${formatAlertType(activeAlert.alert_type)} reported for tourist ${fullTourist?.full_name || 'Unknown'} (Digital ID: ${fullTourist?.digital_id || 'N/A'}) at location ${activeAlert.location?.address || fullTourist?.location?.address || 'Unknown location'}.` :
        `Emergency situation reported for tourist ${fullTourist?.full_name || 'Unknown'} (Digital ID: ${fullTourist?.digital_id || 'N/A'}).`,
      officerName: 'Inspector Raj Kumar', // From current user session
      officerBadge: 'TP-001',
      stationName: 'Tourism Police Station - Darjeeling',
      additionalDetails: activeAlert?.description || '',
      witnesses: '',
      actionTaken: 'Tourist safety monitoring system alert received. Investigation initiated.'
    });
    
    setEfirModalOpen(true);
  };

  const handleEfirInputChange = (field, value) => {
    setEfirData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const generateEFIRNumber = () => {
    const date = new Date();
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const random = Math.floor(Math.random() * 1000).toString().padStart(3, '0');
    return `EFIR/${year}/${month}${day}/${random}`;
  };

  const generateEFIRDocument = () => {
    const efirNumber = generateEFIRNumber();
    const currentDateTime = new Date().toLocaleString();
    
    const efirDocument = `
ELECTRONIC FIRST INFORMATION REPORT (E-FIR)
═══════════════════════════════════════════════════════════════

E-FIR NUMBER: ${efirNumber}
DATE & TIME: ${currentDateTime}
STATION: ${efirData.stationName}

TOURIST INFORMATION:
──────────────────────────────────────────────────────────────
Name: ${fullTourist?.full_name || 'Unknown'}
Digital ID: ${fullTourist?.digital_id || 'N/A'}
Nationality: ${fullTourist?.nationality || 'Unknown'}
Contact: ${fullTourist?.emergency_contacts?.[0]?.phone || 'N/A'}
Current Location: ${fullTourist?.location?.address || 'Unknown'}
Safety Score: ${fullTourist?.safety_score || 0}/100

INCIDENT DETAILS:
──────────────────────────────────────────────────────────────
Type of Incident: ${efirData.incidentType}
Description: ${efirData.incidentDescription}

Additional Details: ${efirData.additionalDetails || 'None'}

Witnesses: ${efirData.witnesses || 'None reported'}

REPORTING OFFICER:
──────────────────────────────────────────────────────────────
Name: ${efirData.officerName}
Badge Number: ${efirData.officerBadge}
Station: ${efirData.stationName}

ACTION TAKEN:
──────────────────────────────────────────────────────────────
${efirData.actionTaken}

ALERT HISTORY:
──────────────────────────────────────────────────────────────
${alerts.length > 0 ? alerts.map(alert => 
  `- ${formatAlertType(alert.alert_type)} (${alert.status}) - ${new Date(alert.created_at).toLocaleString()}`
).join('\n') : 'No alerts on record'}

SYSTEM METADATA:
──────────────────────────────────────────────────────────────
Generated by: Smart Tourist Safety System
Generation Time: ${currentDateTime}
System User: Inspector Raj Kumar (TP-001)

This is an electronically generated document.
═══════════════════════════════════════════════════════════════
    `;

    return { efirNumber, efirDocument };
  };

  const handleDownloadEFIR = () => {
    const { efirNumber, efirDocument } = generateEFIRDocument();
    
    // Create and download the E-FIR as a text file
    const blob = new Blob([efirDocument], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${efirNumber.replace(/\//g, '_')}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    
    setEfirModalOpen(false);
  };

  const handlePrintEFIR = () => {
    const { efirDocument } = generateEFIRDocument();
    
    // Open print window with formatted E-FIR
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
      <html>
        <head>
          <title>E-FIR Document</title>
          <style>
            body { font-family: 'Courier New', monospace; margin: 20px; line-height: 1.6; }
            pre { white-space: pre-wrap; }
          </style>
        </head>
        <body>
          <pre>${efirDocument}</pre>
        </body>
      </html>
    `);
    printWindow.document.close();
    printWindow.print();
  };

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
      <DialogContent className="max-w-[95vw] max-h-[95vh] overflow-y-auto border-4 text-white shadow-2xl" 
                     style={{backgroundColor: '#1F2937', borderColor: '#374151'}}>
        <DialogHeader className="pb-6 border-b-2 -mx-6 -mt-6 px-6 pt-6" 
                      style={{borderColor: '#374151', background: 'linear-gradient(to right, #1F2937, #374151)'}}>
          <div className="flex items-center justify-between">
            <div>
              <DialogTitle className="text-3xl font-black mb-2" style={{color: '#F3F4F6'}}>
                🚨 TOURIST MONITORING REPORT
              </DialogTitle>
              <p className="text-lg font-medium" style={{color: '#9CA3AF'}}>
                Real-time Emergency Operations Dashboard
              </p>
            </div>
            <div className="flex items-center space-x-4">
              {/* Live Status Indicator */}
              <div className="flex items-center space-x-2 px-4 py-2 rounded-lg border-2" 
                   style={{backgroundColor: '#1F2937', borderColor: '#374151'}}>
                <div className="w-3 h-3 rounded-full animate-pulse" style={{backgroundColor: '#22C55E'}}></div>
                <span className="font-bold text-sm" style={{color: '#22C55E'}}>LIVE</span>
              </div>
              <div className={`px-6 py-3 text-xl font-black border-4 rounded`}
                   style={{
                     backgroundColor: getStatusBackgroundColor(fullTourist.status),
                     borderColor: getStatusBorderColor(fullTourist.status),
                     color: '#FFFFFF'
                   }}>
                {fullTourist.status?.toUpperCase() || 'UNKNOWN'}
              </div>
            </div>
          </div>
        </DialogHeader>

        <div className="grid grid-cols-12 gap-8 mt-6">
          {/* Left Column - Identity & Profile */}
          <div className="col-span-12 lg:col-span-4 space-y-6">
            {/* Tourist Identity - Simplified and Clean */}
            <Card className="border-2" style={{backgroundColor: '#1F2937', borderColor: '#374151'}}>
              <CardHeader className="command-card-header pb-4">
                <CardTitle className="text-lg font-bold flex items-center gap-2" style={{color: '#F3F4F6'}}>
                  <CreditCard className="w-6 h-6" />
                  Tourist Identity
                </CardTitle>
              </CardHeader>
              <CardContent className="command-card-content space-y-5">
                <div className="flex items-center space-x-4">
                  <Avatar className="w-24 h-24 ring-4 ring-opacity-50" style={{ringColor: '#3B82F6'}}>
                    <AvatarImage src={fullTourist.photo_url} alt={fullTourist.full_name} />
                    <AvatarFallback className="text-2xl font-bold" style={{backgroundColor: '#3B82F6', color: '#FFFFFF'}}>
                      {fullTourist.full_name ? fullTourist.full_name.split(' ').map(n => n[0]).join('') : 'NA'}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1">
                    <h3 className="text-2xl font-bold mb-2" style={{color: '#F3F4F6'}}>{fullTourist.full_name || 'Unknown'}</h3>
                    <div className="flex items-center space-x-2 mb-3">
                      <Globe className="w-5 h-5" style={{color: '#3B82F6'}} />
                      <span className="text-lg font-medium" style={{color: '#F3F4F6'}}>{fullTourist.nationality || 'Unknown'}</span>
                    </div>
                  </div>
                </div>

                {/* Digital ID - More Prominent */}
                <div className="p-4 rounded-lg border" style={{background: 'linear-gradient(to right, #1E3A8A, #3B82F6)', borderColor: '#3B82F6'}}>
                  <p className="text-xs mb-1 uppercase tracking-wide" style={{color: '#BFDBFE'}}>Digital ID</p>
                  <p className="text-lg font-mono font-bold" style={{color: '#FFFFFF'}}>{fullTourist.digital_id || 'N/A'}</p>
                </div>
              </CardContent>
            </Card>

            {/* Trip Information - Streamlined */}
            <Card className="command-card border-2 border-slate-600" style={{backgroundColor: '#1F2937'}}>
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
            <Card className="command-card border-2 border-slate-600" style={{backgroundColor: '#1F2937'}}>
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

          {/* Center Column - LIVE STATUS & ALERTS (Primary Focus) */}
          <div className="col-span-12 lg:col-span-4 space-y-6">
            {/* MASSIVE STATUS BADGE - Primary Visual Anchor */}
            <Card className="border-4 shadow-2xl" style={{backgroundColor: '#1F2937', borderColor: '#F59E0B'}}>
              <CardContent className="command-card-content text-center py-8">
                {/* HUGE Status Badge */}
                <div className="mb-6">
                  <div className="px-8 py-4 text-4xl font-black uppercase tracking-wider shadow-lg text-center block w-full border-4 rounded-2xl"
                       style={{
                         fontSize: '2.5rem',
                         padding: '1.5rem 2rem',
                         backgroundColor: getStatusBackgroundColor(fullTourist.status),
                         borderColor: getStatusBorderColor(fullTourist.status),
                         color: '#FFFFFF',
                         textShadow: '2px 2px 4px rgba(0,0,0,0.5)'
                       }}>
                    {fullTourist.status?.toUpperCase() || 'UNKNOWN'}
                  </div>
                </div>

                {/* Large Safety Score Circle */}
                <div className="relative w-40 h-40 mx-auto mb-6">
                  <div className="w-40 h-40 rounded-full border-8 flex items-center justify-center relative shadow-2xl" 
                       style={{backgroundColor: '#1F2937', borderColor: '#4B5563'}}>
                    <div className="text-center">
                      <span className="text-5xl font-black" 
                            style={{
                              color: getSafetyScoreColor(fullTourist.safety_score || 0),
                              textShadow: '2px 2px 4px rgba(0,0,0,0.5)'
                            }}>
                        {fullTourist.safety_score || 0}
                      </span>
                      <div className="text-lg font-bold" style={{color: '#9CA3AF'}}>/100</div>
                    </div>
                  </div>
                  {/* Status Ring Indicator */}
                  <div className={`absolute inset-0 rounded-full border-4 ${
                    fullTourist.status === 'panic' ? 'animate-pulse' :
                    fullTourist.status === 'anomaly' ? 'animate-pulse' : ''
                  }`} style={{borderColor: getStatusBackgroundColor(fullTourist.status)}}></div>
                </div>

                {/* Status Description */}
                <div className="p-4 rounded-lg border-2" style={{backgroundColor: '#374151', borderColor: '#4B5563'}}>
                  <p className="text-xs uppercase tracking-wider mb-1" style={{color: '#9CA3AF'}}>Current Status</p>
                  <p className="text-lg font-bold" style={{color: '#F3F4F6'}}>
                    {fullTourist.status === 'panic' ? 'EMERGENCY ALERT ACTIVE' :
                     fullTourist.status === 'anomaly' ? 'MONITORING ANOMALY' :
                     fullTourist.status === 'safe' ? 'ALL SYSTEMS NORMAL' :
                     'STATUS UNKNOWN'}
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Current Location - High Priority Info */}
            <Card className="command-card border-2 border-blue-500" style={{backgroundColor: '#1F2937'}}>
              <CardHeader className="command-card-header pb-3">
                <CardTitle className="modal-section-title text-lg font-bold">
                  <MapPin className="w-6 h-6 text-blue-400" />
                  Current Location
                </CardTitle>
              </CardHeader>
              <CardContent className="command-card-content">
                <div className="bg-slate-700 p-6 rounded-lg border-2 border-slate-500">
                  <div className="flex items-start space-x-4">
                    <MapPin className="w-8 h-8 text-blue-400 mt-1 flex-shrink-0" />
                    <div className="flex-1">
                      <p className="text-lg font-bold text-white mb-2">{fullTourist.location?.address || 'Location updating...'}</p>
                      <div className="flex items-center space-x-2 text-slate-300">
                        <Clock className="w-4 h-4 text-slate-400" />
                        <p className="text-sm">
                          Last update: {fullTourist.location?.timestamp ? new Date(fullTourist.location.timestamp).toLocaleString() : 'Unknown'}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Active Alerts - Critical Information */}
            <Card className="command-card border-2 border-red-500" style={{backgroundColor: '#1F2937'}}>
              <CardHeader className="command-card-header pb-3">
                <CardTitle className="modal-section-title text-lg font-bold">
                  <AlertTriangle className="w-6 h-6 text-red-400" />
                  Active Alerts
                </CardTitle>
              </CardHeader>
              <CardContent className="command-card-content">
                <div className="space-y-4 max-h-80 overflow-y-auto">
                  {alerts?.filter(alert => alert.status === 'new' || alert.status === 'in_progress')?.length > 0 ? (
                    alerts.filter(alert => alert.status === 'new' || alert.status === 'in_progress').map((alert, index) => (
                      <div key={alert.id || index} className="p-4 bg-red-900 rounded-lg border-2 border-red-500 shadow-lg">
                        <div className="flex items-center justify-between mb-3">
                          <Badge className={`px-3 py-1 text-sm font-bold ${getAlertTypeColor(alert.alert_type)}`}
                                 style={{backgroundColor: getAlertTypeBackgroundColor(alert.alert_type)}}>
                            {formatAlertType(alert.alert_type)}
                          </Badge>
                          <Badge className="text-white border-yellow-500 px-3 py-1 text-sm font-bold"
                                 style={{backgroundColor: '#F59E0B'}}>
                            {alert.status.replace('_', ' ').toUpperCase()}
                          </Badge>
                        </div>
                        <p className="text-white font-medium mb-2">{alert.location?.address || 'Location unknown'}</p>
                        <p className="text-red-200 text-sm">
                          {alert.created_at ? new Date(alert.created_at).toLocaleString() : 'Unknown time'}
                        </p>
                        {alert.description && (
                          <p className="text-red-100 text-sm mt-2 bg-red-800 p-2 rounded">{alert.description}</p>
                        )}
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-8 bg-green-900 rounded-lg border-2 border-green-500">
                      <Shield className="w-12 h-12 text-green-400 mx-auto mb-3" />
                      <p className="text-lg font-bold text-green-100">No Active Alerts</p>
                      <p className="text-green-300 text-sm">All systems normal</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Column - History & Response Actions */}
          <div className="col-span-12 lg:col-span-4 space-y-6">
            {/* Location History Trail */}
            <Card className="command-card border-2 border-green-500" style={{backgroundColor: '#1F2937'}}>
              <CardHeader className="command-card-header pb-4">
                <CardTitle className="modal-section-title text-lg font-bold">
                  <MapPin className="w-6 h-6 text-green-400" />
                  Live Trail Map
                </CardTitle>
              </CardHeader>
              <CardContent className="command-card-content">
                <div className="bg-slate-900 p-2 rounded-lg border-2 border-slate-600">
                  <MiniMap 
                    locationHistory={fullTourist.locationHistory}
                    currentLocation={fullTourist.location}
                    className="h-72 rounded-lg"
                  />
                </div>
                <div className="mt-3 text-sm text-slate-300 text-center bg-slate-700 p-2 rounded border border-slate-500">
                  Interactive trail showing recent movement patterns
                </div>
              </CardContent>
            </Card>

            {/* Emergency Response Actions - Operator Focused */}
            <Card className="command-card border-4 border-orange-500 bg-gradient-to-br from-slate-800 to-slate-900">
              <CardHeader className="command-card-header pb-4">
                <CardTitle className="modal-section-title text-xl font-bold text-orange-400">
                  <Shield className="w-7 h-7" />
                  Emergency Response
                </CardTitle>
              </CardHeader>
              <CardContent className="command-card-content">
                <div className="space-y-4">
                  {/* Primary Actions - Large and Prominent */}
                  <div className="grid grid-cols-1 gap-4">
                    <Button className="bg-red-600 hover:bg-red-700 text-white font-bold py-4 px-6 rounded-lg border-2 border-red-400 shadow-lg transition-all hover:shadow-xl text-lg">
                      <Truck className="w-6 h-6 mr-3" />
                      DISPATCH NEAREST UNIT
                    </Button>
                    
                    <Button className="bg-red-800 hover:bg-red-900 text-white font-bold py-4 px-6 rounded-lg border-2 border-red-600 shadow-lg transition-all hover:shadow-xl text-lg">
                      <PhoneCall className="w-6 h-6 mr-3" />
                      CALL EMERGENCY SERVICES
                    </Button>
                  </div>
                  
                  {/* Secondary Actions Grid */}
                  <div className="grid grid-cols-2 gap-3 mt-6">
                    <Button className="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-4 rounded-lg border-2 border-green-400 shadow-lg transition-all hover:shadow-xl">
                      <Shield className="w-5 h-5 mr-2" />
                      MARK SAFE
                    </Button>
                    
                    <Button 
                      onClick={handleCreateEFIR}
                      className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg border-2 border-blue-400 shadow-lg transition-all hover:shadow-xl">
                      <FileText className="w-5 h-5 mr-2" />
                      CREATE E-FIR
                    </Button>
                  </div>

                  {/* Additional Quick Actions */}
                  <div className="grid grid-cols-1 gap-3 mt-4 pt-4 border-t-2 border-slate-600">
                    <Button className="bg-yellow-600 hover:bg-yellow-700 text-white font-bold py-3 px-4 rounded-lg border-2 border-yellow-400 shadow-lg transition-all hover:shadow-xl">
                      <UsersIcon className="w-5 h-5 mr-2" />
                      NOTIFY CONTACTS
                    </Button>
                    
                    <Button className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-4 rounded-lg border-2 border-purple-400 shadow-lg transition-all hover:shadow-xl">
                      <AlertTriangle className="w-5 h-5 mr-2" />
                      ESCALATE ALERT
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Quick Status Actions */}
            <Card className="command-card border-2 border-slate-500" style={{backgroundColor: '#1F2937'}}>
              <CardHeader className="command-card-header pb-3">
                <CardTitle className="modal-section-title text-lg font-bold">
                  <Activity className="w-6 h-6" />
                  Quick Status Updates
                </CardTitle>
              </CardHeader>
              <CardContent className="command-card-content">
                <div className="grid grid-cols-1 gap-2">
                  <Button variant="outline" className="border-slate-500 text-slate-300 hover:bg-slate-700 font-medium py-2">
                    Update Location Manually
                  </Button>
                  <Button variant="outline" className="border-slate-500 text-slate-300 hover:bg-slate-700 font-medium py-2">
                    Request Status Check
                  </Button>
                  <Button variant="outline" className="border-slate-500 text-slate-300 hover:bg-slate-700 font-medium py-2">
                    Generate Report
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </DialogContent>

      {/* E-FIR Generation Modal */}
      <Dialog open={efirModalOpen} onOpenChange={setEfirModalOpen}>
        <DialogContent className="max-w-4xl max-h-[95vh] overflow-y-auto" 
                       style={{backgroundColor: '#1F2937', borderColor: '#374151'}}>
          <DialogHeader className="pb-6 border-b" style={{borderColor: '#374151'}}>
            <DialogTitle className="text-2xl font-bold flex items-center gap-3" style={{color: '#F3F4F6'}}>
              <FileText className="w-7 h-7 text-blue-400" />
              Generate Electronic First Information Report (E-FIR)
            </DialogTitle>
            <p style={{color: '#9CA3AF'}}>
              Create official E-FIR for tourist emergency incident
            </p>
          </DialogHeader>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
            {/* Left Column - Incident Details */}
            <div className="space-y-4">
              <Card style={{backgroundColor: '#374151', borderColor: '#4B5563'}}>
                <CardHeader>
                  <CardTitle style={{color: '#F3F4F6'}}>Incident Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2" style={{color: '#9CA3AF'}}>
                      Incident Type
                    </label>
                    <Select value={efirData.incidentType} onValueChange={(value) => handleEfirInputChange('incidentType', value)}>
                      <SelectTrigger style={{backgroundColor: '#1F2937', borderColor: '#4B5563', color: '#F3F4F6'}}>
                        <SelectValue placeholder="Select incident type" />
                      </SelectTrigger>
                      <SelectContent style={{backgroundColor: '#1F2937', borderColor: '#4B5563'}}>
                        <SelectItem value="Panic Button" style={{color: '#F3F4F6'}}>Panic Button</SelectItem>
                        <SelectItem value="Geofence Breach" style={{color: '#F3F4F6'}}>Geofence Breach</SelectItem>
                        <SelectItem value="Route Deviation" style={{color: '#F3F4F6'}}>Route Deviation</SelectItem>
                        <SelectItem value="Prolonged Inactivity" style={{color: '#F3F4F6'}}>Prolonged Inactivity</SelectItem>
                        <SelectItem value="Missing Person" style={{color: '#F3F4F6'}}>Missing Person</SelectItem>
                        <SelectItem value="Medical Emergency" style={{color: '#F3F4F6'}}>Medical Emergency</SelectItem>
                        <SelectItem value="Theft/Robbery" style={{color: '#F3F4F6'}}>Theft/Robbery</SelectItem>
                        <SelectItem value="Accident" style={{color: '#F3F4F6'}}>Accident</SelectItem>
                        <SelectItem value="Other" style={{color: '#F3F4F6'}}>Other</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2" style={{color: '#9CA3AF'}}>
                      Incident Description
                    </label>
                    <Textarea
                      value={efirData.incidentDescription}
                      onChange={(e) => handleEfirInputChange('incidentDescription', e.target.value)}
                      placeholder="Detailed description of the incident..."
                      rows={4}
                      style={{backgroundColor: '#1F2937', borderColor: '#4B5563', color: '#F3F4F6'}}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2" style={{color: '#9CA3AF'}}>
                      Additional Details
                    </label>
                    <Textarea
                      value={efirData.additionalDetails}
                      onChange={(e) => handleEfirInputChange('additionalDetails', e.target.value)}
                      placeholder="Any additional relevant information..."
                      rows={3}
                      style={{backgroundColor: '#1F2937', borderColor: '#4B5563', color: '#F3F4F6'}}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2" style={{color: '#9CA3AF'}}>
                      Witnesses (if any)
                    </label>
                    <Textarea
                      value={efirData.witnesses}
                      onChange={(e) => handleEfirInputChange('witnesses', e.target.value)}
                      placeholder="Details of witnesses present..."
                      rows={2}
                      style={{backgroundColor: '#1F2937', borderColor: '#4B5563', color: '#F3F4F6'}}
                    />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Right Column - Officer Details & Action */}
            <div className="space-y-4">
              <Card style={{backgroundColor: '#374151', borderColor: '#4B5563'}}>
                <CardHeader>
                  <CardTitle style={{color: '#F3F4F6'}}>Reporting Officer</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2" style={{color: '#9CA3AF'}}>
                      Officer Name
                    </label>
                    <Input
                      value={efirData.officerName}
                      onChange={(e) => handleEfirInputChange('officerName', e.target.value)}
                      placeholder="Officer full name"
                      style={{backgroundColor: '#1F2937', borderColor: '#4B5563', color: '#F3F4F6'}}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2" style={{color: '#9CA3AF'}}>
                      Badge Number
                    </label>
                    <Input
                      value={efirData.officerBadge}
                      onChange={(e) => handleEfirInputChange('officerBadge', e.target.value)}
                      placeholder="Officer badge/ID number"
                      style={{backgroundColor: '#1F2937', borderColor: '#4B5563', color: '#F3F4F6'}}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2" style={{color: '#9CA3AF'}}>
                      Police Station
                    </label>
                    <Input
                      value={efirData.stationName}
                      onChange={(e) => handleEfirInputChange('stationName', e.target.value)}
                      placeholder="Police station name"
                      style={{backgroundColor: '#1F2937', borderColor: '#4B5563', color: '#F3F4F6'}}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2" style={{color: '#9CA3AF'}}>
                      Action Taken
                    </label>
                    <Textarea
                      value={efirData.actionTaken}
                      onChange={(e) => handleEfirInputChange('actionTaken', e.target.value)}
                      placeholder="Describe actions taken or planned..."
                      rows={4}
                      style={{backgroundColor: '#1F2937', borderColor: '#4B5563', color: '#F3F4F6'}}
                    />
                  </div>
                </CardContent>
              </Card>

              {/* Tourist Summary */}
              <Card style={{backgroundColor: '#374151', borderColor: '#4B5563'}}>
                <CardHeader>
                  <CardTitle style={{color: '#F3F4F6'}}>Tourist Summary</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span style={{color: '#9CA3AF'}}>Name:</span>
                      <span style={{color: '#F3F4F6'}}>{fullTourist?.full_name || 'Unknown'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span style={{color: '#9CA3AF'}}>Digital ID:</span>
                      <span style={{color: '#F3F4F6'}}>{fullTourist?.digital_id || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span style={{color: '#9CA3AF'}}>Nationality:</span>
                      <span style={{color: '#F3F4F6'}}>{fullTourist?.nationality || 'Unknown'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span style={{color: '#9CA3AF'}}>Status:</span>
                      <span style={{color: getStatusBackgroundColor(fullTourist?.status)}}>
                        {fullTourist?.status?.toUpperCase() || 'UNKNOWN'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span style={{color: '#9CA3AF'}}>Location:</span>
                      <span style={{color: '#F3F4F6'}} className="text-right max-w-48 truncate">
                        {fullTourist?.location?.address || 'Unknown'}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end space-x-4 mt-6 pt-6 border-t" style={{borderColor: '#374151'}}>
            <Button 
              variant="outline" 
              onClick={() => setEfirModalOpen(false)}
              className="border-slate-500 text-slate-300 hover:bg-slate-700"
            >
              Cancel
            </Button>
            <Button 
              onClick={handlePrintEFIR}
              className="bg-gray-600 hover:bg-gray-700 text-white"
            >
              <Printer className="w-4 h-4 mr-2" />
              Print E-FIR
            </Button>
            <Button 
              onClick={handleDownloadEFIR}
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              <Download className="w-4 h-4 mr-2" />
              Download E-FIR
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </Dialog>
  );
};

export default TouristDetailModal;