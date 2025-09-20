/**
 * E-FIR Documents Page
 * Main page for managing Electronic First Information Reports
 */

import React, { useState, useEffect } from 'react';
import { 
  Plus, Search, Filter, FileText, Eye, Edit, Trash2, 
  Download, Signature, Clock, AlertTriangle, CheckCircle 
} from 'lucide-react';
import { efirAPI, EFIR_TYPES, EFIR_PRIORITIES, EFIR_STATUSES } from '../services/efirAPI';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { useToast } from '../hooks/use-toast';
import { useNavigate } from 'react-router-dom';

const EFIRDocuments = () => {
  const [efirDocuments, setEfirDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    fir_type: '',
    status: '',
    priority: '',
    created_by: ''
  });
  const [showFilters, setShowFilters] = useState(false);
  const { toast } = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    loadEFIRDocuments();
  }, [filters]);

  const loadEFIRDocuments = async () => {
    setLoading(true);
    try {
      const result = await efirAPI.getEFIRList(filters);
      if (result.success) {
        setEfirDocuments(result.data);
      } else {
        toast({
          title: "Error",
          description: result.error,
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load E-FIR documents",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      loadEFIRDocuments();
      return;
    }

    setLoading(true);
    try {
      const result = await efirAPI.searchEFIR(searchQuery, filters);
      if (result.success) {
        setEfirDocuments(result.data);
      } else {
        toast({
          title: "Error",
          description: result.error,
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to search E-FIR documents",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteEFIR = async (efirId, firNumber) => {
    if (!window.confirm(`Are you sure you want to delete E-FIR ${firNumber}? This action cannot be undone.`)) {
      return;
    }

    try {
      const result = await efirAPI.deleteEFIR(efirId);
      if (result.success) {
        toast({
          title: "Success",
          description: "E-FIR document deleted successfully",
        });
        loadEFIRDocuments();
      } else {
        toast({
          title: "Error",
          description: result.error,
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete E-FIR document",
        variant: "destructive",
      });
    }
  };

  const handleDownloadPDF = async (efirId, firNumber) => {
    try {
      const result = await efirAPI.downloadPDF(efirId);
      if (result.success) {
        toast({
          title: "Success",
          description: "PDF downloaded successfully",
        });
      } else {
        toast({
          title: "Error",
          description: result.error,
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to download PDF",
        variant: "destructive",
      });
    }
  };

  const getPriorityColor = (priority) => {
    const priorityObj = EFIR_PRIORITIES.find(p => p.value === priority);
    return priorityObj?.color || 'text-gray-600 bg-gray-100';
  };

  const getStatusColor = (status) => {
    const statusObj = EFIR_STATUSES.find(s => s.value === status);
    return statusObj?.color || 'text-gray-600 bg-gray-100';
  };

  const getTypeLabel = (type) => {
    const typeObj = EFIR_TYPES.find(t => t.value === type);
    return typeObj?.label || type;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="h-full flex flex-col" style={{backgroundColor: '#111827'}}>
      {/* Header */}
      <div className="flex-shrink-0 p-6 border-b" style={{borderColor: '#374151'}}>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold" style={{color: '#F3F4F6'}}>E-FIR Documents</h1>
            <p style={{color: '#9CA3AF'}}>Electronic First Information Reports Management</p>
          </div>
          <Button
            onClick={() => navigate('/efir/create')}
            className="bg-blue-600 hover:bg-blue-700 text-white"
          >
            <Plus className="w-4 h-4 mr-2" />
            Create New E-FIR
          </Button>
        </div>

        {/* Search and Filters */}
        <div className="flex flex-col sm:flex-row gap-4 mb-4">
          <div className="flex-1 flex gap-2">
            <Input
              placeholder="Search E-FIR documents..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              className="flex-1 border"
              style={{
                backgroundColor: '#1F2937',
                borderColor: '#374151',
                color: '#F3F4F6'
              }}
            />
            <Button onClick={handleSearch} variant="outline" 
              style={{
                borderColor: '#374151',
                color: '#9CA3AF',
                backgroundColor: 'transparent'
              }}>
              <Search className="w-4 h-4" />
            </Button>
          </div>
          <Button
            onClick={() => setShowFilters(!showFilters)}
            variant="outline"
            className="sm:w-auto"
            style={{
              borderColor: '#374151',
              color: '#9CA3AF',
              backgroundColor: 'transparent'
            }}
          >
            <Filter className="w-4 h-4 mr-2" />
            Filters
          </Button>
        </div>

        {/* Filter Panel */}
        {showFilters && (
          <Card className="mb-4 border" style={{backgroundColor: '#1F2937', borderColor: '#374151'}}>
            <CardContent className="pt-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div>
                  <label className="text-sm font-medium mb-1 block" style={{color: '#9CA3AF'}}>Type</label>
                  <select
                    value={filters.fir_type}
                    onChange={(e) => setFilters({ ...filters, fir_type: e.target.value })}
                    className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    style={{
                      backgroundColor: '#374151',
                      borderColor: '#4B5563',
                      color: '#F3F4F6'
                    }}
                  >
                    <option value="">All Types</option>
                    {EFIR_TYPES.map(type => (
                      <option key={type.value} value={type.value}>{type.label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="text-sm font-medium mb-1 block" style={{color: '#9CA3AF'}}>Status</label>
                  <select
                    value={filters.status}
                    onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                    className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    style={{
                      backgroundColor: '#374151',
                      borderColor: '#4B5563',
                      color: '#F3F4F6'
                    }}
                  >
                    <option value="">All Statuses</option>
                    {EFIR_STATUSES.map(status => (
                      <option key={status.value} value={status.value}>{status.label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="text-sm font-medium mb-1 block" style={{color: '#9CA3AF'}}>Priority</label>
                  <select
                    value={filters.priority}
                    onChange={(e) => setFilters({ ...filters, priority: e.target.value })}
                    className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    style={{
                      backgroundColor: '#374151',
                      borderColor: '#4B5563',
                      color: '#F3F4F6'
                    }}
                  >
                    <option value="">All Priorities</option>
                    {EFIR_PRIORITIES.map(priority => (
                      <option key={priority.value} value={priority.value}>{priority.label}</option>
                    ))}
                  </select>
                </div>
                <div className="flex items-end">
                  <Button
                    onClick={() => {
                      setFilters({ fir_type: '', status: '', priority: '', created_by: '' });
                      setSearchQuery('');
                    }}
                    variant="outline"
                    className="w-full"
                    style={{
                      borderColor: '#374151',
                      color: '#9CA3AF',
                      backgroundColor: 'transparent'
                    }}
                  >
                    Clear Filters
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Documents List */}
      <div className="flex-1 overflow-auto p-6">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-2" style={{color: '#9CA3AF'}}>Loading E-FIR documents...</span>
          </div>
        ) : efirDocuments.length === 0 ? (
          <Card className="border" style={{backgroundColor: '#1F2937', borderColor: '#374151'}}>
            <CardContent className="text-center py-12">
              <FileText className="w-12 h-12 mx-auto mb-4" style={{color: '#6B7280'}} />
              <h3 className="text-lg font-medium mb-2" style={{color: '#F3F4F6'}}>No E-FIR Documents Found</h3>
              <p className="mb-4" style={{color: '#9CA3AF'}}>
                {searchQuery || Object.values(filters).some(f => f) 
                  ? "Try adjusting your search criteria or filters."
                  : "Get started by creating your first E-FIR document."
                }
              </p>
              <Button
                onClick={() => navigate('/efir/create')}
                className="bg-blue-600 hover:bg-blue-700 text-white"
              >
                <Plus className="w-4 h-4 mr-2" />
                Create New E-FIR
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4">
            {efirDocuments.map((efir) => (
              <Card key={efir.id} className="hover:shadow-md transition-shadow border" 
                style={{backgroundColor: '#1F2937', borderColor: '#374151'}}>
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold" style={{color: '#F3F4F6'}}>{efir.fir_number}</h3>
                        <Badge className={getPriorityColor(efir.priority)}>
                          {EFIR_PRIORITIES.find(p => p.value === efir.priority)?.label || efir.priority}
                        </Badge>
                        <Badge className={getStatusColor(efir.status)}>
                          {EFIR_STATUSES.find(s => s.value === efir.status)?.label || efir.status}
                        </Badge>
                        {efir.signatures && efir.signatures.length > 0 && (
                          <Badge className="text-green-600 bg-green-100">
                            <Signature className="w-3 h-3 mr-1" />
                            Signed ({efir.signatures.length})
                          </Badge>
                        )}
                      </div>
                      <h4 className="text-md font-medium mb-2" style={{color: '#E5E7EB'}}>{efir.title}</h4>
                      <p className="text-sm mb-2" style={{color: '#9CA3AF'}}>{getTypeLabel(efir.fir_type)}</p>
                      <p className="text-sm line-clamp-2 mb-3" style={{color: '#9CA3AF'}}>{efir.incident_description}</p>
                      <div className="flex items-center gap-4 text-xs" style={{color: '#9CA3AF'}}>
                        <span>Created: {formatDate(efir.created_at)}</span>
                        <span>Version: {efir.current_version}</span>
                        <span>By: {efir.created_by}</span>
                        {efir.incident_date && (
                          <span>Incident: {formatDate(efir.incident_date)}</span>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2 ml-4">
                      <Button
                        onClick={() => navigate(`/efir/${efir.id}`)}
                        size="sm"
                        variant="outline"
                        title="View Details"
                        style={{
                          borderColor: '#374151',
                          color: '#9CA3AF',
                          backgroundColor: 'transparent'
                        }}
                      >
                        <Eye className="w-4 h-4" />
                      </Button>
                      <Button
                        onClick={() => navigate(`/efir/${efir.id}/edit`)}
                        size="sm"
                        variant="outline"
                        title="Edit"
                        style={{
                          borderColor: '#374151',
                          color: '#9CA3AF',
                          backgroundColor: 'transparent'
                        }}
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button
                        onClick={() => handleDownloadPDF(efir.id, efir.fir_number)}
                        size="sm"
                        variant="outline"
                        title="Download PDF"
                        style={{
                          borderColor: '#374151',
                          color: '#9CA3AF',
                          backgroundColor: 'transparent'
                        }}
                      >
                        <Download className="w-4 h-4" />
                      </Button>
                      <Button
                        onClick={() => navigate(`/efir/${efir.id}/history`)}
                        size="sm"
                        variant="outline"
                        title="View History"
                        style={{
                          borderColor: '#374151',
                          color: '#9CA3AF',
                          backgroundColor: 'transparent'
                        }}
                      >
                        <Clock className="w-4 h-4" />
                      </Button>
                      <Button
                        onClick={() => handleDeleteEFIR(efir.id, efir.fir_number)}
                        size="sm"
                        variant="outline"
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        title="Delete"
                        style={{
                          borderColor: '#374151',
                          color: '#EF4444',
                          backgroundColor: 'transparent'
                        }}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Results Summary */}
        {!loading && efirDocuments.length > 0 && (
          <div className="mt-6 text-center text-sm" style={{color: '#9CA3AF'}}>
            Showing {efirDocuments.length} E-FIR document{efirDocuments.length !== 1 ? 's' : ''}
          </div>
        )}
      </div>
    </div>
  );
};

export default EFIRDocuments;