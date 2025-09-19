import React, { useState, useEffect } from 'react';
import { Search, Filter, Download, Plus, MapPin, Phone } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Avatar, AvatarImage, AvatarFallback } from '../components/ui/avatar';
import { touristsAPI } from '../services/api';

const TouristDatabase = ({ onTouristSelect }) => {
  const [tourists, setTourists] = useState([]);
  const [filteredTourists, setFilteredTourists] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    status: 'all',
    nationality: 'all',
    search: ''
  });

  // Load tourists when component mounts
  useEffect(() => {
    loadTourists();
  }, []);

  const loadTourists = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await touristsAPI.getTourists({ limit: 100 });
      setTourists(data);
      setFilteredTourists(data);
    } catch (err) {
      console.error('Error loading tourists:', err);
      setError('Failed to load tourists');
      setTourists([]);
      setFilteredTourists([]);
    } finally {
      setLoading(false);
    }
  };

  const statusTypes = [
    { value: 'all', label: 'All Status' },
    { value: 'safe', label: 'Safe' },
    { value: 'anomaly', label: 'Anomaly' },
    { value: 'panic', label: 'Panic Alert' }
  ];

  const nationalities = [
    { value: 'all', label: 'All Countries' },
    { value: 'USA', label: 'United States' },
    { value: 'Spain', label: 'Spain' },
    { value: 'Japan', label: 'Japan' },
    { value: 'UK', label: 'United Kingdom' },
    { value: 'Germany', label: 'Germany' },
    { value: 'France', label: 'France' }
  ];

  const getStatusBadge = (status) => {
    const configs = {
      safe: 'status-badge-safe',
      anomaly: 'status-badge-anomaly', 
      panic: 'status-badge-panic'
    };
    return configs[status] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const handleFilterChange = (key, value) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    
    let filtered = tourists;
    
    if (newFilters.status !== 'all') {
      filtered = filtered.filter(tourist => tourist.status === newFilters.status);
    }
    
    if (newFilters.nationality !== 'all') {
      filtered = filtered.filter(tourist => tourist.nationality === newFilters.nationality);
    }
    
    if (newFilters.search) {
      filtered = filtered.filter(tourist => 
        (tourist.full_name || '').toLowerCase().includes(newFilters.search.toLowerCase()) ||
        (tourist.digital_id || '').toLowerCase().includes(newFilters.search.toLowerCase()) ||
        (tourist.nationality || '').toLowerCase().includes(newFilters.search.toLowerCase())
      );
    }
    
    setFilteredTourists(filtered);
  };

  return (
    <div className="h-full flex flex-col bg-slate-900">
      {/* Enhanced Header Section */}
      <div className="p-6 border-b border-slate-700">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h1 className="page-title mb-2">Tourist Database</h1>
            <p className="text-slate-400 text-sm">Comprehensive tourist registry and management system</p>
          </div>
          <div className="flex space-x-3">
            <Button variant="outline" className="border-slate-600 text-slate-300 hover:bg-slate-700">
              <Download className="w-4 h-4 mr-2" />
              Export Data
            </Button>
            <Button className="action-btn-primary">
              <Plus className="w-4 h-4 mr-2" />
              Add Tourist
            </Button>
          </div>
        </div>

        {/* Enhanced Filter Controls */}
        <div className="flex flex-wrap gap-4 items-center mb-4">
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-slate-400" />
            <span className="text-sm font-medium text-slate-300">Filters:</span>
          </div>
          
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

          <Select value={filters.nationality} onValueChange={(value) => handleFilterChange('nationality', value)}>
            <SelectTrigger className="w-48 bg-slate-800 border-slate-600 text-white">
              <SelectValue placeholder="Select nationality" />
            </SelectTrigger>
            <SelectContent className="bg-slate-800 border-slate-600">
              {nationalities.map(country => (
                <SelectItem key={country.value} value={country.value} className="text-white">
                  {country.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
            <Input
              placeholder="Search tourists..."
              value={filters.search}
              onChange={(e) => handleFilterChange('search', e.target.value)}
              className="pl-10 w-64 bg-slate-800 border-slate-600 text-white placeholder-slate-400"
            />
          </div>
        </div>

        <div className="text-sm text-slate-400">
          Showing <span className="font-semibold text-white">{filteredTourists.length}</span> of <span className="font-semibold text-white">{tourists.length}</span> tourists
        </div>
      </div>

      {/* Enhanced Tourist Grid */}
      <div className="flex-1 overflow-auto p-6">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
              <p className="text-slate-400">Loading tourists...</p>
            </div>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="text-red-500 mb-4">❌</div>
              <p className="text-slate-400">{error}</p>
              <Button onClick={loadTourists} className="mt-4">
                Try Again
              </Button>
            </div>
          </div>
        ) : filteredTourists.length === 0 ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <p className="text-slate-400">No tourists found</p>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {filteredTourists.map((tourist) => (
            <Card key={tourist.id} className="tourist-card">
              <CardContent className="tourist-card-content">
                {/* Header with Avatar, Name, and Status Badge */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3 flex-1">
                    <Avatar className="w-12 h-12 ring-2 ring-slate-600">
                      <AvatarImage src={tourist.photo_url} alt={tourist.full_name} />
                      <AvatarFallback className="bg-blue-600 text-white font-semibold">
                        {tourist.full_name ? tourist.full_name.split(' ').map(n => n[0]).join('') : 'NA'}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2">
                        <h3 className="font-semibold text-white truncate">{tourist.full_name || 'Unknown'}</h3>
                        <Badge className={getStatusBadge(tourist.status)}>
                          {tourist.status?.toUpperCase() || 'UNKNOWN'}
                        </Badge>
                      </div>
                      <p className="text-sm text-slate-400 flex items-center">
                        {tourist.nationality || 'Unknown'}
                      </p>
                      <p className="text-xs text-slate-500 font-mono">{tourist.digital_id || 'N/A'}</p>
                    </div>
                  </div>
                </div>

                {/* Location and Contact Info */}
                <div className="space-y-3 mb-4">
                  <div className="flex items-start text-sm text-slate-300">
                    <MapPin className="w-4 h-4 mr-2 text-slate-400 mt-0.5 flex-shrink-0" />
                    <span className="truncate">{tourist.location?.address || 'Location not available'}</span>
                  </div>
                  
                  <div className="flex items-center text-sm text-slate-300">
                    <Phone className="w-4 h-4 mr-2 text-slate-400 flex-shrink-0" />
                    <span className="truncate">{tourist.emergency_contacts?.[0]?.phone || 'N/A'}</span>
                  </div>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-2 gap-4 mb-4 p-3 bg-slate-700 rounded-lg">
                  <div className="text-center">
                    <p className="text-xs text-slate-400 mb-1">Safety Score</p>
                    <div className={`text-lg font-bold ${
                      (tourist.safety_score || 0) >= 80 ? 'text-emerald-400' :
                      (tourist.safety_score || 0) >= 50 ? 'text-amber-400' : 'text-red-400'
                    }`}>
                      {tourist.safety_score || 0}/100
                    </div>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-slate-400 mb-1">Visit Duration</p>
                    <div className="text-lg font-bold text-white">
                      {tourist.visit_end_date && tourist.visit_start_date ? 
                        Math.ceil((new Date(tourist.visit_end_date) - new Date(tourist.visit_start_date)) / (1000 * 60 * 60 * 24)) : 0} days
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex space-x-2">
                  <Button
                    size="sm"
                    onClick={() => onTouristSelect(tourist)}
                    className="flex-1 action-btn-primary text-sm py-2"
                  >
                    View Details
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    className="border-slate-600 text-slate-300 hover:bg-slate-700 px-3"
                    title="Show on Map"
                  >
                    <MapPin className="w-4 h-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default TouristDatabase;