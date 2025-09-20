/**
 * E-FIR Form Component
 * For creating and editing E-FIR documents
 */

import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Save, FileText, MapPin, Clock, Users, AlertTriangle } from 'lucide-react';
import { efirAPI, EFIR_TYPES, EFIR_PRIORITIES, EFIR_STATUSES } from '../services/efirAPI';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Textarea } from '../components/ui/textarea';
import { useToast } from '../hooks/use-toast';

const EFIRForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const isEdit = Boolean(id);

  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    fir_type: 'tourist_incident',
    priority: 'medium',
    status: 'draft',
    incident_date: '',
    incident_location: {
      coordinates: {
        type: 'Point',
        coordinates: [0, 0]
      },
      address: '',
      timestamp: new Date().toISOString()
    },
    incident_description: '',
    related_tourist_id: '',
    related_alert_id: '',
    complainant_name: '',
    complainant_contact: '',
    accused_details: '',
    witness_details: '',
    case_details: '',
    evidence_details: '',
    action_taken: '',
    changes_summary: ''
  });

  useEffect(() => {
    if (isEdit) {
      loadEFIRDocument();
    } else {
      // Set default incident date to current date/time
      setFormData(prev => ({
        ...prev,
        incident_date: new Date().toISOString().slice(0, 16) // Format for datetime-local input
      }));
    }
  }, [id, isEdit]);

  const loadEFIRDocument = async () => {
    setLoading(true);
    try {
      const result = await efirAPI.getEFIR(id);
      if (result.success) {
        const data = result.data;
        setFormData({
          title: data.title || '',
          fir_type: data.fir_type || 'tourist_incident',
          priority: data.priority || 'medium',
          status: data.status || 'draft',
          incident_date: data.incident_date ? new Date(data.incident_date).toISOString().slice(0, 16) : '',
          incident_location: data.incident_location || {
            coordinates: { type: 'Point', coordinates: [0, 0] },
            address: '',
            timestamp: new Date().toISOString()
          },
          incident_description: data.incident_description || '',
          related_tourist_id: data.related_tourist_id || '',
          related_alert_id: data.related_alert_id || '',
          complainant_name: data.complainant_name || '',
          complainant_contact: data.complainant_contact || '',
          accused_details: data.accused_details || '',
          witness_details: data.witness_details || '',
          case_details: data.case_details || '',
          evidence_details: data.evidence_details || '',
          action_taken: data.action_taken || '',
          changes_summary: ''
        });
      } else {
        toast({
          title: "Error",
          description: result.error,
          variant: "destructive",
        });
        navigate('/efir');
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load E-FIR document",
        variant: "destructive",
      });
      navigate('/efir');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field, value) => {
    if (field.includes('.')) {
      const [parent, child] = field.split('.');
      setFormData(prev => ({
        ...prev,
        [parent]: {
          ...prev[parent],
          [child]: value
        }
      }));
    } else if (field === 'coordinates') {
      // Handle coordinates input as "lat,lng"
      const [lat, lng] = value.split(',').map(v => parseFloat(v.trim()));
      if (!isNaN(lat) && !isNaN(lng)) {
        setFormData(prev => ({
          ...prev,
          incident_location: {
            ...prev.incident_location,
            coordinates: {
              type: 'Point',
              coordinates: [lng, lat] // GeoJSON format: [longitude, latitude]
            }
          }
        }));
      }
    } else {
      setFormData(prev => ({
        ...prev,
        [field]: value
      }));
    }
  };

  const validateForm = () => {
    const required = ['title', 'incident_description', 'case_details'];
    const missing = required.filter(field => !formData[field]?.trim());
    
    if (missing.length > 0) {
      toast({
        title: "Validation Error",
        description: `Please fill in required fields: ${missing.join(', ')}`,
        variant: "destructive",
      });
      return false;
    }

    if (isEdit && !formData.changes_summary?.trim()) {
      toast({
        title: "Validation Error",
        description: "Please provide a summary of changes for version tracking",
        variant: "destructive",
      });
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setSaving(true);
    try {
      // Prepare data for submission
      const submitData = {
        ...formData,
        incident_date: new Date(formData.incident_date).toISOString(),
        incident_location: {
          ...formData.incident_location,
          timestamp: new Date().toISOString()
        }
      };

      let result;
      if (isEdit) {
        result = await efirAPI.updateEFIR(id, submitData);
      } else {
        // Remove changes_summary for new documents
        const { changes_summary, ...createData } = submitData;
        result = await efirAPI.createEFIR(createData);
      }

      if (result.success) {
        toast({
          title: "Success",
          description: `E-FIR document ${isEdit ? 'updated' : 'created'} successfully`,
        });
        navigate('/efir');
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
        description: `Failed to ${isEdit ? 'update' : 'create'} E-FIR document`,
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">Loading E-FIR document...</span>
      </div>
    );
  }

  const currentCoordinates = formData.incident_location?.coordinates?.coordinates || [0, 0];
  const coordinatesDisplay = `${currentCoordinates[1]}, ${currentCoordinates[0]}`; // lat, lng for display

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-4 mb-4">
          <Button
            onClick={() => navigate('/efir')}
            variant="outline"
            size="sm"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to E-FIR Documents
          </Button>
        </div>
        <div className="flex items-center gap-3">
          <FileText className="w-8 h-8 text-blue-600" />
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              {isEdit ? 'Edit E-FIR Document' : 'Create New E-FIR Document'}
            </h1>
            <p className="text-gray-600">Electronic First Information Report</p>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5" />
              Basic Information
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-700 mb-1 block">
                  Title <span className="text-red-500">*</span>
                </label>
                <Input
                  value={formData.title}
                  onChange={(e) => handleInputChange('title', e.target.value)}
                  placeholder="Enter E-FIR title"
                  required
                />
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700 mb-1 block">Type</label>
                <select
                  value={formData.fir_type}
                  onChange={(e) => handleInputChange('fir_type', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {EFIR_TYPES.map(type => (
                    <option key={type.value} value={type.value}>{type.label}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700 mb-1 block">Priority</label>
                <select
                  value={formData.priority}
                  onChange={(e) => handleInputChange('priority', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {EFIR_PRIORITIES.map(priority => (
                    <option key={priority.value} value={priority.value}>{priority.label}</option>
                  ))}
                </select>
              </div>
              {isEdit && (
                <div>
                  <label className="text-sm font-medium text-gray-700 mb-1 block">Status</label>
                  <select
                    value={formData.status}
                    onChange={(e) => handleInputChange('status', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {EFIR_STATUSES.map(status => (
                      <option key={status.value} value={status.value}>{status.label}</option>
                    ))}
                  </select>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Incident Details */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5" />
              Incident Details
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-700 mb-1 block">Incident Date & Time</label>
                <Input
                  type="datetime-local"
                  value={formData.incident_date}
                  onChange={(e) => handleInputChange('incident_date', e.target.value)}
                />
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700 mb-1 block">
                  Location Coordinates (Lat, Lng)
                </label>
                <Input
                  value={coordinatesDisplay}
                  onChange={(e) => handleInputChange('coordinates', e.target.value)}
                  placeholder="e.g., 27.0400, 88.2700"
                />
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 mb-1 block">Address</label>
              <Input
                value={formData.incident_location?.address || ''}
                onChange={(e) => handleInputChange('incident_location.address', e.target.value)}
                placeholder="Enter incident location address"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 mb-1 block">
                Incident Description <span className="text-red-500">*</span>
              </label>
              <Textarea
                value={formData.incident_description}
                onChange={(e) => handleInputChange('incident_description', e.target.value)}
                placeholder="Describe the incident in detail"
                rows={4}
                required
              />
            </div>
          </CardContent>
        </Card>

        {/* Parties Involved */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="w-5 h-5" />
              Parties Involved
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-700 mb-1 block">Complainant Name</label>
                <Input
                  value={formData.complainant_name}
                  onChange={(e) => handleInputChange('complainant_name', e.target.value)}
                  placeholder="Enter complainant name"
                />
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700 mb-1 block">Complainant Contact</label>
                <Input
                  value={formData.complainant_contact}
                  onChange={(e) => handleInputChange('complainant_contact', e.target.value)}
                  placeholder="Enter contact information"
                />
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 mb-1 block">Accused Details</label>
              <Textarea
                value={formData.accused_details}
                onChange={(e) => handleInputChange('accused_details', e.target.value)}
                placeholder="Describe the accused person(s)"
                rows={3}
              />
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 mb-1 block">Witness Details</label>
              <Textarea
                value={formData.witness_details}
                onChange={(e) => handleInputChange('witness_details', e.target.value)}
                placeholder="Describe witnesses and their contact information"
                rows={3}
              />
            </div>
          </CardContent>
        </Card>

        {/* Case Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5" />
              Case Information
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-700 mb-1 block">
                Case Details <span className="text-red-500">*</span>
              </label>
              <Textarea
                value={formData.case_details}
                onChange={(e) => handleInputChange('case_details', e.target.value)}
                placeholder="Provide detailed case information"
                rows={4}
                required
              />
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 mb-1 block">Evidence Details</label>
              <Textarea
                value={formData.evidence_details}
                onChange={(e) => handleInputChange('evidence_details', e.target.value)}
                placeholder="Describe evidence collected"
                rows={3}
              />
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 mb-1 block">Action Taken</label>
              <Textarea
                value={formData.action_taken}
                onChange={(e) => handleInputChange('action_taken', e.target.value)}
                placeholder="Describe actions taken"
                rows={3}
              />
            </div>
          </CardContent>
        </Card>

        {/* Related Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MapPin className="w-5 h-5" />
              Related Information
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-700 mb-1 block">Related Tourist ID</label>
                <Input
                  value={formData.related_tourist_id}
                  onChange={(e) => handleInputChange('related_tourist_id', e.target.value)}
                  placeholder="Enter tourist ID if applicable"
                />
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700 mb-1 block">Related Alert ID</label>
                <Input
                  value={formData.related_alert_id}
                  onChange={(e) => handleInputChange('related_alert_id', e.target.value)}
                  placeholder="Enter alert ID if applicable"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Version Information for Edit */}
        {isEdit && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="w-5 h-5" />
                Version Information
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div>
                <label className="text-sm font-medium text-gray-700 mb-1 block">
                  Changes Summary <span className="text-red-500">*</span>
                </label>
                <Textarea
                  value={formData.changes_summary}
                  onChange={(e) => handleInputChange('changes_summary', e.target.value)}
                  placeholder="Describe the changes made in this version"
                  rows={3}
                  required
                />
                <p className="text-xs text-gray-500 mt-1">
                  This information will be used for version tracking and audit purposes.
                </p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Form Actions */}
        <div className="flex items-center justify-end gap-4 pt-6 border-t">
          <Button
            type="button"
            variant="outline"
            onClick={() => navigate('/efir')}
            disabled={saving}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            className="bg-blue-600 hover:bg-blue-700 text-white"
            disabled={saving}
          >
            {saving ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                {isEdit ? 'Updating...' : 'Creating...'}
              </>
            ) : (
              <>
                <Save className="w-4 h-4 mr-2" />
                {isEdit ? 'Update E-FIR' : 'Create E-FIR'}
              </>
            )}
          </Button>
        </div>
      </form>
    </div>
  );
};

export default EFIRForm;