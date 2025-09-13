import React, { useState } from 'react';
import { Filter, Calendar, Search } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { mockAlerts } from '../mock';

const Alerts = ({ onTouristSelect }) => {
  const [alerts, setAlerts] = useState(mockAlerts);
  const [filteredAlerts, setFilteredAlerts] = useState(mockAlerts);
  const [filters, setFilters] = useState({
    type: 'all',
    status: 'all',
    search: ''
  });

  const alertTypes = [
    { value: 'all', label: 'All Types' },
    { value: 'panic_button', label: 'Panic Button' },
    { value: 'geofence_breach', label: 'Geo-fence Breach' },
    { value: 'route_deviation', label: 'Route Deviation' },
    { value: 'prolonged_inactivity', label: 'Prolonged Inactivity' }
  ];

  const statusTypes = [
    { value: 'all', label: 'All Status' },
    { value: 'new', label: 'New' },
    { value: 'in_progress', label: 'In Progress' },
    { value: 'resolved', label: 'Resolved' }
  ];

  const getAlertTypeBadge = (type) => {
    const configs = {
      panic_button: 'bg-red-100 text-red-800 border-red-200',
      geofence_breach: 'bg-red-100 text-red-800 border-red-200',
      route_deviation: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      prolonged_inactivity: 'bg-yellow-100 text-yellow-800 border-yellow-200'
    };
    return configs[type] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const getStatusBadge = (status) => {
    const configs = {
      new: 'bg-red-100 text-red-800 border-red-200',
      in_progress: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      resolved: 'bg-green-100 text-green-800 border-green-200'
    };
    return configs[status] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const formatAlertType = (type) => {
    return type.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  const handleFilterChange = (key, value) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    
    let filtered = alerts;
    
    if (newFilters.type !== 'all') {
      filtered = filtered.filter(alert => alert.type === newFilters.type);
    }
    
    if (newFilters.status !== 'all') {
      filtered = filtered.filter(alert => alert.status === newFilters.status);
    }
    
    if (newFilters.search) {
      filtered = filtered.filter(alert => 
        alert.touristName.toLowerCase().includes(newFilters.search.toLowerCase()) ||
        alert.id.toLowerCase().includes(newFilters.search.toLowerCase()) ||
        alert.location.toLowerCase().includes(newFilters.search.toLowerCase())
      );
    }
    
    setFilteredAlerts(filtered);
  };

  const handleTouristView = (alertId) => {
    const alert = alerts.find(a => a.id === alertId);
    if (alert && alert.touristId) {
      // In real app, fetch tourist details by ID
      onTouristSelect({ id: alert.touristId, name: alert.touristName });
    }
  };

  return (
    <div className="h-full flex flex-col bg-slate-900">
      {/* Header Section */}
      <div className="p-6 border-b border-slate-700">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-white">Incident & Alert History</h1>
          <div className="text-sm text-slate-400">
            Showing {filteredAlerts.length} of {alerts.length} alerts
          </div>
        </div>

        {/* Filter Controls */}
        <div className="flex flex-wrap gap-4 items-center">
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-slate-400" />
            <span className="text-sm text-slate-300">Filters:</span>
          </div>
          
          <Select value={filters.type} onValueChange={(value) => handleFilterChange('type', value)}>
            <SelectTrigger className="w-48 bg-slate-800 border-slate-600 text-white">
              <SelectValue placeholder="Select alert type" />
            </SelectTrigger>
            <SelectContent className="bg-slate-800 border-slate-600">
              {alertTypes.map(type => (
                <SelectItem key={type.value} value={type.value} className="text-white">
                  {type.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={filters.status} onValueChange={(value) => handleFilterChange('status', value)}>
            <SelectTrigger className="w-40 bg-slate-800 border-slate-600 text-white">
              <SelectValue placeholder="Select status" />
            </SelectTrigger>
            <SelectContent className="bg-slate-800 border-slate-600">
              {statusTypes.map(status => (
                <SelectItem key={status.value} value={status.value} className="text-white">
                  {status.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
            <Input
              placeholder="Search alerts..."
              value={filters.search}
              onChange={(e) => handleFilterChange('search', e.target.value)}
              className="pl-10 w-64 bg-slate-800 border-slate-600 text-white placeholder-slate-400"
            />
          </div>
        </div>
      </div>

      {/* Alerts Table */}
      <div className="flex-1 overflow-auto p-6">
        <Card className="bg-slate-800 border-slate-700">
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow className="border-slate-700 hover:bg-slate-700">
                  <TableHead className="text-slate-300">Alert ID</TableHead>
                  <TableHead className="text-slate-300">Tourist Name</TableHead>
                  <TableHead className="text-slate-300">Alert Type</TableHead>
                  <TableHead className="text-slate-300">Location</TableHead>
                  <TableHead className="text-slate-300">Timestamp</TableHead>
                  <TableHead className="text-slate-300">Status</TableHead>
                  <TableHead className="text-slate-300">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredAlerts.map((alert) => (
                  <TableRow key={alert.id} className="border-slate-700 hover:bg-slate-700">
                    <TableCell className="font-medium text-white">{alert.id}</TableCell>
                    <TableCell className="text-slate-300">{alert.touristName}</TableCell>
                    <TableCell>
                      <Badge className={getAlertTypeBadge(alert.type)}>
                        {formatAlertType(alert.type)}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-slate-300">{alert.location}</TableCell>
                    <TableCell className="text-slate-400">
                      {new Date(alert.timestamp).toLocaleString()}
                    </TableCell>
                    <TableCell>
                      <Badge className={getStatusBadge(alert.status)}>
                        {alert.status.charAt(0).toUpperCase() + alert.status.slice(1).replace('_', ' ')}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleTouristView(alert.id)}
                        className="border-slate-600 text-slate-300 hover:bg-slate-700 hover:text-white"
                      >
                        View Details
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {filteredAlerts.length === 0 && (
          <div className="text-center py-12">
            <div className="text-slate-400 text-lg mb-2">No alerts found</div>
            <div className="text-slate-500 text-sm">Try adjusting your filters</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Alerts;