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

  const nationalityTypes = [
    { value: 'all', label: 'All Countries' },
    { value: 'India', label: 'India' },
    { value: 'USA', label: 'USA' },
    { value: 'UK', label: 'UK' },
    { value: 'Bangladesh', label: 'Bangladesh' }
  ];

  // Filter tourists based on current filters
  useEffect(() => {
    let filtered = tourists;

    if (filters.status !== 'all') {
      filtered = filtered.filter(tourist => tourist.status === filters.status);
    }

    if (filters.nationality !== 'all') {
      filtered = filtered.filter(tourist => tourist.nationality === filters.nationality);
    }

    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      filtered = filtered.filter(tourist =>
        tourist.full_name?.toLowerCase().includes(searchLower) ||
        tourist.digital_id?.toLowerCase().includes(searchLower) ||
        tourist.nationality?.toLowerCase().includes(searchLower)
      );
    }

    setFilteredTourists(filtered);
  }, [tourists, filters]);

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const getStatusBadge = (status) => {
    const getStatusStyle = (status) => {
      switch (status) {
        case 'safe':
          return {
            backgroundColor: '#22C55E', // Safe Green
            color: '#FFFFFF',
            border: '2px solid #16A34A'
          };
        case 'anomaly':
          return {
            backgroundColor: '#F59E0B', // Warning Amber
            color: '#FFFFFF',
            border: '2px solid #D97706'
          };
        case 'panic':
          return {
            backgroundColor: '#EF4444', // Panic Red
            color: '#FFFFFF',
            border: '2px solid #DC2626'
          };
        default:
          return {
            backgroundColor: '#6B7280',
            color: '#FFFFFF',
            border: '2px solid #4B5563'
          };
      }
    };

    return (
      <span 
        className="px-3 py-1 text-sm font-bold rounded"
        style={getStatusStyle(status)}
      >
        {status?.toUpperCase() || 'UNKNOWN'}
      </span>
    );
  };

  const getSafetyScoreColor = (score) => {
    if (score >= 80) return '#22C55E'; // Safe Green
    if (score >= 50) return '#F59E0B'; // Warning Amber
    return '#EF4444'; // Panic Red
  };

  return (
    <div className="h-full flex flex-col" style={{backgroundColor: '#111827'}}>
      {/* Header with Filters */}
      <div className="flex-shrink-0 p-6 border-b" style={{borderColor: '#374151'}}>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold" style={{color: '#F3F4F6'}}>Tourist Database</h1>
            <p style={{color: '#9CA3AF'}}>Comprehensive tourist registry and management system</p>
          </div>
          <div className="flex space-x-3">
            <Button className="action-btn-primary">
              <Download className="w-4 h-4 mr-2" />
              Export Data
            </Button>
            <Button className="action-btn-success">
              <Plus className="w-4 h-4 mr-2" />
              Add Tourist
            </Button>
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4" style={{color: '#9CA3AF'}} />
            <span className="text-sm font-medium" style={{color: '#9CA3AF'}}>Filters:</span>
          </div>
          
          <Select value={filters.status} onValueChange={(value) => handleFilterChange('status', value)}>
            <SelectTrigger className="w-48 border" style={{backgroundColor: '#1F2937', borderColor: '#374151', color: '#F3F4F6'}}>
              <SelectValue placeholder="All Status" />
            </SelectTrigger>
            <SelectContent style={{backgroundColor: '#1F2937', borderColor: '#374151'}}>
              {statusTypes.map((status) => (
                <SelectItem key={status.value} value={status.value} style={{color: '#F3F4F6'}}>
                  {status.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={filters.nationality} onValueChange={(value) => handleFilterChange('nationality', value)}>
            <SelectTrigger className="w-48 border" style={{backgroundColor: '#1F2937', borderColor: '#374151', color: '#F3F4F6'}}>
              <SelectValue placeholder="All Countries" />
            </SelectTrigger>
            <SelectContent style={{backgroundColor: '#1F2937', borderColor: '#374151'}}>
              {nationalityTypes.map((nationality) => (
                <SelectItem key={nationality.value} value={nationality.value} style={{color: '#F3F4F6'}}>
                  {nationality.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4" style={{color: '#9CA3AF'}} />
            <Input
              placeholder="Search tourists..."
              value={filters.search}
              onChange={(e) => handleFilterChange('search', e.target.value)}
              className="pl-10 w-64 border"
              style={{
                backgroundColor: '#1F2937',
                borderColor: '#374151',
                color: '#F3F4F6'
              }}
            />
          </div>
        </div>

        <div className="text-sm mt-4" style={{color: '#9CA3AF'}}>
          Showing <span className="font-semibold" style={{color: '#F3F4F6'}}>{filteredTourists.length}</span> of <span className="font-semibold" style={{color: '#F3F4F6'}}>{tourists.length}</span> tourists
        </div>
      </div>

      {/* Enhanced Tourist Grid */}
      <div className="flex-1 overflow-auto p-6">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 mx-auto mb-4" style={{borderColor: '#3B82F6'}}></div>
              <p style={{color: '#9CA3AF'}}>Loading tourists...</p>
            </div>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="mb-4" style={{color: '#EF4444'}}>❌</div>
              <p style={{color: '#9CA3AF'}} className="mb-4">{error}</p>
              <Button onClick={loadTourists} className="action-btn-primary">
                Try Again
              </Button>
            </div>
          </div>
        ) : filteredTourists.length === 0 ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <p style={{color: '#9CA3AF'}}>No tourists found</p>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-6 auto-rows-fr">
            {filteredTourists.map((tourist) => (
            <Card key={tourist.id} className="tourist-card h-full flex flex-col">
              <CardContent className="tourist-card-content flex-1 flex flex-col">
                {/* Header with Avatar, Name, and Status Badge */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3 flex-1">
                    <Avatar className="w-12 h-12 ring-2" style={{ringColor: '#374151'}}>
                      <AvatarImage src={tourist.photo_url} alt={tourist.full_name} />
                      <AvatarFallback className="font-semibold" style={{backgroundColor: '#3B82F6', color: '#FFFFFF'}}>
                        {tourist.full_name ? tourist.full_name.split(' ').map(n => n[0]).join('') : 'NA'}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2">
                        <h3 className="font-semibold truncate" style={{color: '#F3F4F6'}}>{tourist.full_name || 'Unknown'}</h3>
                        {getStatusBadge(tourist.status)}
                      </div>
                      <p className="text-sm flex items-center" style={{color: '#9CA3AF'}}>
                        {tourist.nationality || 'Unknown'}
                      </p>
                      <p className="text-xs font-mono" style={{color: '#9CA3AF'}}>{tourist.digital_id || 'N/A'}</p>
                    </div>
                  </div>
                </div>

                {/* Location and Contact Info */}
                <div className="space-y-3 mb-4 flex-1">
                  <div className="flex items-start text-sm" style={{color: '#9CA3AF'}}>
                    <MapPin className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" style={{color: '#9CA3AF'}} />
                    <span className="truncate">{tourist.location?.address || 'Location not available'}</span>
                  </div>
                  
                  <div className="flex items-center text-sm" style={{color: '#9CA3AF'}}>
                    <Phone className="w-4 h-4 mr-2 flex-shrink-0" style={{color: '#9CA3AF'}} />
                    <span className="truncate">{tourist.emergency_contacts?.[0]?.phone || 'N/A'}</span>
                  </div>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-2 gap-4 mb-4 p-3 rounded-lg" style={{backgroundColor: '#374151'}}>
                  <div className="text-center">
                    <p className="text-xs mb-1" style={{color: '#9CA3AF'}}>Safety Score</p>
                    <div className={`text-lg font-bold`}
                         style={{color: getSafetyScoreColor(tourist.safety_score || 0)}}>
                      {tourist.safety_score || 0}/100
                    </div>
                  </div>
                  <div className="text-center">
                    <p className="text-xs mb-1" style={{color: '#9CA3AF'}}>Visit Duration</p>
                    <div className="text-lg font-bold" style={{color: '#F3F4F6'}}>
                      {tourist.visit_end_date && tourist.visit_start_date ? 
                        Math.ceil((new Date(tourist.visit_end_date) - new Date(tourist.visit_start_date)) / (1000 * 60 * 60 * 24)) : 0} days
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex space-x-2 mt-auto">
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
                    className="px-3 transition-colors"
                    style={{
                      borderColor: '#374151',
                      color: '#9CA3AF',
                      backgroundColor: 'transparent'
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.backgroundColor = '#374151';
                      e.target.style.color = '#F3F4F6';
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.backgroundColor = 'transparent';  
                      e.target.style.color = '#9CA3AF';
                    }}
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