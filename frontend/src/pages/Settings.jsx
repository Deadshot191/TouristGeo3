import React, { useState } from 'react';
import { Settings as SettingsIcon, Bell, Shield, Map, Users, Save, AlertTriangle, Globe, Clock } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Switch } from '../components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Separator } from '../components/ui/separator';
import { Badge } from '../components/ui/badge';

const Settings = () => {
  const [settings, setSettings] = useState({
    notifications: {
      panicAlerts: true,
      geofenceBreaches: true,
      routeDeviations: false,
      inactivityAlerts: true,
      emailNotifications: true,
      smsNotifications: false,
    },
    system: {
      autoRefreshInterval: '30',
      mapProvider: 'google',
      defaultZoomLevel: '12',
      language: 'english',
      timezone: 'IST',
    },
    security: {
      sessionTimeout: '60',
      requireTwoFactor: false,
      logSensitiveActions: true,
      dataRetentionDays: '365',
    },
    thresholds: {
      inactivityMinutes: '30',
      panicResponseTime: '5',
      safetyScoreThreshold: '50',
      geofenceBuffer: '100',
    }
  });

  const handleSettingChange = (category, key, value) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [key]: value
      }
    }));
  };

  const handleSaveSettings = () => {
    // In real app, this would save to backend
    console.log('Saving settings:', settings);
    // Show success notification
  };

  return (
    <div className="h-full flex flex-col bg-slate-900">
      {/* Header */}
      <div className="p-6 border-b border-slate-700">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <SettingsIcon className="w-8 h-8 text-blue-400" />
            <div>
              <h1 className="text-2xl font-bold text-white">System Settings</h1>
              <p className="text-slate-400">Configure dashboard preferences and security settings</p>
            </div>
          </div>
          <Button onClick={handleSaveSettings} className="bg-blue-600 hover:bg-blue-700 text-white">
            <Save className="w-4 h-4 mr-2" />
            Save Changes
          </Button>
        </div>
      </div>

      {/* Settings Content */}
      <div className="flex-1 overflow-auto p-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* Notification Settings */}
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader>
              <CardTitle className="flex items-center text-white">
                <Bell className="w-5 h-5 mr-2 text-blue-400" />
                Notification Settings
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label className="text-white">Panic Alerts</Label>
                    <p className="text-sm text-slate-400">Immediate notifications for panic button activations</p>
                  </div>
                  <Switch
                    checked={settings.notifications.panicAlerts}
                    onCheckedChange={(value) => handleSettingChange('notifications', 'panicAlerts', value)}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label className="text-white">Geo-fence Breaches</Label>
                    <p className="text-sm text-slate-400">Alerts when tourists enter restricted areas</p>
                  </div>
                  <Switch
                    checked={settings.notifications.geofenceBreaches}
                    onCheckedChange={(value) => handleSettingChange('notifications', 'geofenceBreaches', value)}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label className="text-white">Route Deviations</Label>
                    <p className="text-sm text-slate-400">Notifications for unexpected route changes</p>
                  </div>
                  <Switch
                    checked={settings.notifications.routeDeviations}
                    onCheckedChange={(value) => handleSettingChange('notifications', 'routeDeviations', value)}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label className="text-white">Inactivity Alerts</Label>
                    <p className="text-sm text-slate-400">Warnings for prolonged periods without movement</p>
                  </div>
                  <Switch
                    checked={settings.notifications.inactivityAlerts}
                    onCheckedChange={(value) => handleSettingChange('notifications', 'inactivityAlerts', value)}
                  />
                </div>

                <Separator className="bg-slate-600" />

                <div className="flex items-center justify-between">
                  <div>
                    <Label className="text-white">Email Notifications</Label>
                    <p className="text-sm text-slate-400">Send alerts via email</p>
                  </div>
                  <Switch
                    checked={settings.notifications.emailNotifications}
                    onCheckedChange={(value) => handleSettingChange('notifications', 'emailNotifications', value)}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label className="text-white">SMS Notifications</Label>
                    <p className="text-sm text-slate-400">Send alerts via SMS</p>
                  </div>
                  <Switch
                    checked={settings.notifications.smsNotifications}
                    onCheckedChange={(value) => handleSettingChange('notifications', 'smsNotifications', value)}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* System Settings */}
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader>
              <CardTitle className="flex items-center text-white">
                <SettingsIcon className="w-5 h-5 mr-2 text-blue-400" />
                System Configuration
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-4">
                <div>
                  <Label className="text-white">Auto Refresh Interval (seconds)</Label>
                  <Select
                    value={settings.system.autoRefreshInterval}
                    onValueChange={(value) => handleSettingChange('system', 'autoRefreshInterval', value)}
                  >
                    <SelectTrigger className="bg-slate-700 border-slate-600 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-700 border-slate-600">
                      <SelectItem value="15" className="text-white">15 seconds</SelectItem>
                      <SelectItem value="30" className="text-white">30 seconds</SelectItem>
                      <SelectItem value="60" className="text-white">1 minute</SelectItem>
                      <SelectItem value="300" className="text-white">5 minutes</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label className="text-white">Map Provider</Label>
                  <Select
                    value={settings.system.mapProvider}
                    onValueChange={(value) => handleSettingChange('system', 'mapProvider', value)}
                  >
                    <SelectTrigger className="bg-slate-700 border-slate-600 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-700 border-slate-600">
                      <SelectItem value="google" className="text-white">Google Maps</SelectItem>
                      <SelectItem value="mapbox" className="text-white">Mapbox</SelectItem>
                      <SelectItem value="openstreet" className="text-white">OpenStreetMap</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label className="text-white">Default Zoom Level</Label>
                  <Select
                    value={settings.system.defaultZoomLevel}
                    onValueChange={(value) => handleSettingChange('system', 'defaultZoomLevel', value)}
                  >
                    <SelectTrigger className="bg-slate-700 border-slate-600 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-700 border-slate-600">
                      <SelectItem value="10" className="text-white">City Level (10)</SelectItem>
                      <SelectItem value="12" className="text-white">District Level (12)</SelectItem>
                      <SelectItem value="14" className="text-white">Neighborhood (14)</SelectItem>
                      <SelectItem value="16" className="text-white">Street Level (16)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label className="text-white">Interface Language</Label>
                  <Select
                    value={settings.system.language}
                    onValueChange={(value) => handleSettingChange('system', 'language', value)}
                  >
                    <SelectTrigger className="bg-slate-700 border-slate-600 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-700 border-slate-600">
                      <SelectItem value="english" className="text-white">English</SelectItem>
                      <SelectItem value="hindi" className="text-white">Hindi</SelectItem>
                      <SelectItem value="bengali" className="text-white">Bengali</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Security Settings */}
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader>
              <CardTitle className="flex items-center text-white">
                <Shield className="w-5 h-5 mr-2 text-blue-400" />
                Security Settings
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-4">
                <div>
                  <Label className="text-white">Session Timeout (minutes)</Label>
                  <Input
                    type="number"
                    value={settings.security.sessionTimeout}
                    onChange={(e) => handleSettingChange('security', 'sessionTimeout', e.target.value)}
                    className="bg-slate-700 border-slate-600 text-white"
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label className="text-white">Require Two-Factor Authentication</Label>
                    <p className="text-sm text-slate-400">Additional security for officer logins</p>
                  </div>
                  <Switch
                    checked={settings.security.requireTwoFactor}
                    onCheckedChange={(value) => handleSettingChange('security', 'requireTwoFactor', value)}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label className="text-white">Log Sensitive Actions</Label>
                    <p className="text-sm text-slate-400">Track all critical operations</p>
                  </div>
                  <Switch
                    checked={settings.security.logSensitiveActions}
                    onCheckedChange={(value) => handleSettingChange('security', 'logSensitiveActions', value)}
                  />
                </div>

                <div>
                  <Label className="text-white">Data Retention Period (days)</Label>
                  <Input
                    type="number"
                    value={settings.security.dataRetentionDays}
                    onChange={(e) => handleSettingChange('security', 'dataRetentionDays', e.target.value)}
                    className="bg-slate-700 border-slate-600 text-white"
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Alert Thresholds */}
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader>
              <CardTitle className="flex items-center text-white">
                <AlertTriangle className="w-5 h-5 mr-2 text-blue-400" />
                Alert Thresholds
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-4">
                <div>
                  <Label className="text-white">Inactivity Alert Threshold (minutes)</Label>
                  <Input
                    type="number"
                    value={settings.thresholds.inactivityMinutes}
                    onChange={(e) => handleSettingChange('thresholds', 'inactivityMinutes', e.target.value)}
                    className="bg-slate-700 border-slate-600 text-white"
                  />
                </div>

                <div>
                  <Label className="text-white">Panic Response Time (minutes)</Label>
                  <Input
                    type="number"
                    value={settings.thresholds.panicResponseTime}
                    onChange={(e) => handleSettingChange('thresholds', 'panicResponseTime', e.target.value)}
                    className="bg-slate-700 border-slate-600 text-white"
                  />
                </div>

                <div>
                  <Label className="text-white">Safety Score Alert Threshold</Label>
                  <Input
                    type="number"
                    value={settings.thresholds.safetyScoreThreshold}
                    onChange={(e) => handleSettingChange('thresholds', 'safetyScoreThreshold', e.target.value)}
                    className="bg-slate-700 border-slate-600 text-white"
                  />
                  <p className="text-sm text-slate-400 mt-1">Alert when safety score falls below this value</p>
                </div>

                <div>
                  <Label className="text-white">Geo-fence Buffer Distance (meters)</Label>
                  <Input
                    type="number"
                    value={settings.thresholds.geofenceBuffer}
                    onChange={(e) => handleSettingChange('thresholds', 'geofenceBuffer', e.target.value)}
                    className="bg-slate-700 border-slate-600 text-white"
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* System Status */}
        <Card className="bg-slate-800 border-slate-700 mt-6">
          <CardHeader>
            <CardTitle className="flex items-center text-white">
              <Globe className="w-5 h-5 mr-2 text-blue-400" />
              System Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="flex items-center justify-between p-3 bg-slate-700 rounded-lg">
                <div>
                  <p className="text-sm text-slate-400">API Status</p>
                  <p className="text-white font-medium">Operational</p>
                </div>
                <Badge className="bg-green-100 text-green-800 border-green-200">Online</Badge>
              </div>
              
              <div className="flex items-center justify-between p-3 bg-slate-700 rounded-lg">
                <div>
                  <p className="text-sm text-slate-400">Database</p>
                  <p className="text-white font-medium">Connected</p>
                </div>
                <Badge className="bg-green-100 text-green-800 border-green-200">Active</Badge>
              </div>
              
              <div className="flex items-center justify-between p-3 bg-slate-700 rounded-lg">
                <div>
                  <p className="text-sm text-slate-400">GPS Services</p>
                  <p className="text-white font-medium">Available</p>
                </div>
                <Badge className="bg-green-100 text-green-800 border-green-200">Active</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Settings;