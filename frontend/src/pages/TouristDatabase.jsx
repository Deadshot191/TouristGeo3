import React, { useState } from 'react';
import { Search, Filter, Download, Plus, MapPin, Phone } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Avatar, AvatarImage, AvatarFallback } from '../components/ui/avatar';
import { mockTourists } from '../mock';

const TouristDatabase = ({ onTouristSelect }) => {
  const [tourists, setTourists] = useState(mockTourists);
  const [filteredTourists, setFilteredTourists] = useState(mockTourists);
  const [filters, setFilters] = useState({
    status: 'all',
    nationality: 'all',
    search: ''
  });

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
        tourist.name.toLowerCase().includes(newFilters.search.toLowerCase()) ||
        tourist.digitalId.toLowerCase().includes(newFilters.search.toLowerCase()) ||
        tourist.nationality.toLowerCase().includes(newFilters.search.toLowerCase())
      );
    }
    
    setFilteredTourists(filtered);
  };

  return (
    <div className="h-full flex flex-col bg-slate-900">
      {/* Header Section */}
      <div className="p-6 border-b border-slate-700">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-white">Tourist Database</h1>
          <div className="flex space-x-2">
            <Button variant="outline" className="border-slate-600 text-slate-300 hover:bg-slate-700">
              <Download className="w-4 h-4 mr-2" />
              Export Data
            </Button>
            <Button className="bg-blue-600 hover:bg-blue-700 text-white">
              <Plus className="w-4 h-4 mr-2" />
              Add Tourist
            </Button>
          </div>
        </div>

        {/* Filter Controls */}
        <div className="flex flex-wrap gap-4 items-center">
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-slate-400" />
            <span className="text-sm text-slate-300">Filters:</span>
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

        <div className="mt-4 text-sm text-slate-400">
          Showing {filteredTourists.length} of {tourists.length} tourists
        </div>
      </div>

      {/* Tourist Grid */}
      <div className="flex-1 overflow-auto p-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {filteredTourists.map((tourist) => (
            <Card key={tourist.id} className="bg-slate-800 border-slate-700 hover:bg-slate-750 transition-colors">
              <CardContent className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <Avatar className="w-12 h-12">
                      <AvatarImage src={tourist.photo} alt={tourist.name} />
                      <AvatarFallback className="bg-blue-600 text-white">
                        {tourist.name.split(' ').map(n => n[0]).join('')}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <h3 className="font-semibold text-white">{tourist.name}</h3>
                      <p className="text-sm text-slate-400">{tourist.nationality}</p>
                      <p className="text-xs text-slate-500 font-mono">{tourist.digitalId}</p>
                    </div>
                  </div>
                  <Badge className={getStatusBadge(tourist.status)}>
                    {tourist.status.toUpperCase()}
                  </Badge>
                </div>

                <div className="space-y-2 mb-4">
                  <div className="flex items-center text-sm text-slate-300">
                    <MapPin className="w-4 h-4 mr-2 text-slate-400" />
                    <span className="truncate">{tourist.location?.address}</span>
                  </div>
                  
                  <div className="flex items-center text-sm text-slate-300">
                    <Phone className="w-4 h-4 mr-2 text-slate-400" />
                    <span>{tourist.emergencyContacts?.[0]?.phone || 'N/A'}</span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
                  <div>
                    <p className="text-slate-400">Safety Score</p>
                    <p className="text-white font-semibold">{tourist.safetyScore}/100</p>
                  </div>
                  <div>
                    <p className="text-slate-400">Visit Duration</p>
                    <p className="text-white font-semibold">
                      {Math.ceil((new Date(tourist.visitEndDate) - new Date(tourist.visitStartDate)) / (1000 * 60 * 60 * 24))} days
                    </p>
                  </div>
                </div>

                <div className="flex space-x-2">
                  <Button
                    size="sm"
                    onClick={() => onTouristSelect(tourist)}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
                  >
                    View Details
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    className="border-slate-600 text-slate-300 hover:bg-slate-700"
                  >
                    <MapPin className="w-4 h-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {filteredTourists.length === 0 && (
          <div className="text-center py-12">
            <div className="text-slate-400 text-lg mb-2">No tourists found</div>
            <div className="text-slate-500 text-sm">Try adjusting your filters</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TouristDatabase;