/**
 * E-FIR Detail Page
 * Displays detailed view of an E-FIR document with actions
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, Edit, Download, Signature, Clock, FileText, 
  MapPin, Users, AlertTriangle, CheckCircle, Shield, QrCode 
} from 'lucide-react';
import { efirAPI, EFIR_TYPES, EFIR_PRIORITIES, EFIR_STATUSES } from '../services/efirAPI';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { useToast } from '../hooks/use-toast';
import { useAuth } from '../contexts/AuthContext';

const EFIRDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const { user } = useAuth();
  
  const [efir, setEfir] = useState(null);
  const [loading, setLoading] = useState(true);
  const [signing, setSigning] = useState(false);
  const [signPassword, setSignPassword] = useState('');
  const [showSignDialog, setShowSignDialog] = useState(false);

  useEffect(() => {
    loadEFIRDocument();
  }, [id]);

  const loadEFIRDocument = async () => {
    setLoading(true);
    try {
      const result = await efirAPI.getEFIR(id);
      if (result.success) {
        setEfir(result.data);
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

  const handleDownloadPDF = async () => {
    try {
      const result = await efirAPI.downloadPDF(id);
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

  const handleGeneratePDF = async () => {
    try {
      const result = await efirAPI.generatePDF(id);
      if (result.success) {
        toast({
          title: "Success",
          description: "PDF generated successfully",
        });
        // Reload document to update PDF status
        loadEFIRDocument();
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
        description: "Failed to generate PDF",
        variant: "destructive",
      });
    }
  };

  const handleSignDocument = async () => {
    if (!signPassword.trim()) {
      toast({
        title: "Error",
        description: "Please enter your password to sign the document",
        variant: "destructive",
      });
      return;
    }

    setSigning(true);
    try {
      const result = await efirAPI.signEFIR(id, signPassword);
      if (result.success) {
        toast({
          title: "Success",
          description: "Document signed successfully",
        });
        setShowSignDialog(false);
        setSignPassword('');
        // Reload document to show new signature
        loadEFIRDocument();
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
        description: "Failed to sign document",
        variant: "destructive",
      });
    } finally {
      setSigning(false);
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
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const isAlreadySigned = efir?.signatures?.some(sig => sig.officer_id === user?.email);

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center" style={{backgroundColor: '#111827'}}>
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2" style={{color: '#9CA3AF'}}>Loading E-FIR document...</span>
      </div>
    );
  }

  if (!efir) {
    return (
      <div className="h-full flex flex-col" style={{backgroundColor: '#111827'}}>
        <div className="flex-1 flex items-center justify-center p-6">
          <Card className="border" style={{backgroundColor: '#1F2937', borderColor: '#374151'}}>
            <CardContent className="text-center py-12">
              <FileText className="w-12 h-12 mx-auto mb-4" style={{color: '#6B7280'}} />
              <h3 className="text-lg font-medium mb-2" style={{color: '#F3F4F6'}}>E-FIR Document Not Found</h3>
              <p className="mb-4" style={{color: '#9CA3AF'}}>The requested E-FIR document could not be found.</p>
              <Button onClick={() => navigate('/efir')} className="bg-blue-600 hover:bg-blue-700 text-white">
                Back to E-FIR Documents
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col" style={{backgroundColor: '#111827'}}>
      {/* Header */}
      <div className="flex-shrink-0 p-6 border-b" style={{borderColor: '#374151'}}>
        <div className="flex items-center gap-4 mb-4">
          <Button
            onClick={() => navigate('/efir')}
            variant="outline"
            size="sm"
            style={{
              borderColor: '#374151',
              color: '#9CA3AF',
              backgroundColor: 'transparent'
            }}
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to E-FIR Documents
          </Button>
        </div>
        
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            <FileText className="w-8 h-8 text-blue-600" />
            <div>
              <h1 className="text-3xl font-bold" style={{color: '#F3F4F6'}}>{efir.fir_number}</h1>
              <p className="text-lg" style={{color: '#9CA3AF'}}>{efir.title}</p>
              <div className="flex items-center gap-2 mt-2">
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
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              onClick={() => navigate(`/efir/${id}/edit`)}
              variant="outline"
              size="sm"
              style={{
                borderColor: '#374151',
                color: '#9CA3AF',
                backgroundColor: 'transparent'
              }}
            >
              <Edit className="w-4 h-4 mr-2" />
              Edit
            </Button>
            <Button
              onClick={handleDownloadPDF}
              variant="outline"
              size="sm"
              style={{
                borderColor: '#374151',
                color: '#9CA3AF',
                backgroundColor: 'transparent'
              }}
            >
              <Download className="w-4 h-4 mr-2" />
              Download PDF
            </Button>
            {!efir.has_pdf && (
              <Button
                onClick={handleGeneratePDF}
                variant="outline"
                size="sm"
                style={{
                  borderColor: '#374151',
                  color: '#9CA3AF',
                  backgroundColor: 'transparent'
                }}
              >
                <FileText className="w-4 h-4 mr-2" />
                Generate PDF
              </Button>
            )}
            <Dialog open={showSignDialog} onOpenChange={setShowSignDialog}>
              <DialogTrigger asChild>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={isAlreadySigned}
                  className={isAlreadySigned ? "opacity-50" : ""}
                  style={{
                    borderColor: '#374151',
                    color: isAlreadySigned ? '#6B7280' : '#9CA3AF',
                    backgroundColor: 'transparent'
                  }}
                >
                  <Signature className="w-4 h-4 mr-2" />
                  {isAlreadySigned ? 'Already Signed' : 'Sign Document'}
                </Button>
              </DialogTrigger>
              <DialogContent style={{backgroundColor: '#1F2937', borderColor: '#374151'}}>
                <DialogHeader>
                  <DialogTitle style={{color: '#F3F4F6'}}>Digital Signature</DialogTitle>
                </DialogHeader>
                <div className="space-y-4">
                  <p className="text-sm" style={{color: '#9CA3AF'}}>
                    Enter your password to digitally sign this E-FIR document.
                  </p>
                  <div>
                    <label className="text-sm font-medium mb-1 block" style={{color: '#9CA3AF'}}>
                      Password
                    </label>
                    <Input
                      type="password"
                      value={signPassword}
                      onChange={(e) => setSignPassword(e.target.value)}
                      placeholder="Enter your password"
                      style={{
                        backgroundColor: '#374151',
                        borderColor: '#4B5563',
                        color: '#F3F4F6'
                      }}
                    />
                  </div>
                  <div className="flex justify-end gap-2">
                    <Button
                      variant="outline"
                      onClick={() => {
                        setShowSignDialog(false);
                        setSignPassword('');
                      }}
                      style={{
                        borderColor: '#374151',
                        color: '#9CA3AF',
                        backgroundColor: 'transparent'
                      }}
                    >
                      Cancel
                    </Button>
                    <Button
                      onClick={handleSignDocument}
                      disabled={signing || !signPassword.trim()}
                      className="bg-blue-600 hover:bg-blue-700 text-white"
                    >
                      {signing ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                          Signing...
                        </>
                      ) : (
                        <>
                          <Signature className="w-4 h-4 mr-2" />
                          Sign Document
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
            <Button
              onClick={() => navigate(`/efir/${id}/history`)}
              variant="outline"
              size="sm"
              style={{
                borderColor: '#374151',
                color: '#9CA3AF',
                backgroundColor: 'transparent'
              }}
            >
              <Clock className="w-4 h-4 mr-2" />
              History
            </Button>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-4xl mx-auto grid gap-6">
          {/* Document Information */}
          <Card className="border" style={{backgroundColor: '#1F2937', borderColor: '#374151'}}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2" style={{color: '#F3F4F6'}}>
                <FileText className="w-5 h-5" />
                Document Information
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div>
                  <label className="text-sm font-medium" style={{color: '#9CA3AF'}}>FIR Number</label>
                  <p className="text-sm font-mono px-2 py-1 rounded" style={{backgroundColor: '#374151', color: '#F3F4F6'}}>{efir.fir_number}</p>
                </div>
                <div>
                  <label className="text-sm font-medium" style={{color: '#9CA3AF'}}>Type</label>
                  <p className="text-sm" style={{color: '#F3F4F6'}}>{getTypeLabel(efir.fir_type)}</p>
                </div>
                <div>
                  <label className="text-sm font-medium" style={{color: '#9CA3AF'}}>Version</label>
                  <p className="text-sm" style={{color: '#F3F4F6'}}>{efir.current_version}</p>
                </div>
                <div>
                  <label className="text-sm font-medium" style={{color: '#9CA3AF'}}>Created By</label>
                  <p className="text-sm" style={{color: '#F3F4F6'}}>{efir.created_by}</p>
                </div>
                <div>
                  <label className="text-sm font-medium" style={{color: '#9CA3AF'}}>Created Date</label>
                  <p className="text-sm" style={{color: '#F3F4F6'}}>{formatDate(efir.created_at)}</p>
                </div>
                <div>
                  <label className="text-sm font-medium" style={{color: '#9CA3AF'}}>PDF Status</label>
                  <p className="text-sm" style={{color: '#F3F4F6'}}>{efir.has_pdf ? 'Generated' : 'Not Generated'}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Incident Details */}
          <Card className="border" style={{backgroundColor: '#1F2937', borderColor: '#374151'}}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2" style={{color: '#F3F4F6'}}>
                <AlertTriangle className="w-5 h-5" />
                Incident Details
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium" style={{color: '#9CA3AF'}}>Incident Date</label>
                  <p className="text-sm" style={{color: '#F3F4F6'}}>{formatDate(efir.incident_date)}</p>
                </div>
                <div>
                  <label className="text-sm font-medium" style={{color: '#9CA3AF'}}>Location</label>
                  <p className="text-sm" style={{color: '#F3F4F6'}}>
                    {efir.incident_location?.address || 'No address provided'}
                    {efir.incident_location?.coordinates && (
                      <span className="block text-xs font-mono" style={{color: '#9CA3AF'}}>
                        {efir.incident_location.coordinates.coordinates[1].toFixed(6)}, 
                        {efir.incident_location.coordinates.coordinates[0].toFixed(6)}
                      </span>
                    )}
                  </p>
                </div>
              </div>
              <div>
                <label className="text-sm font-medium" style={{color: '#9CA3AF'}}>Description</label>
                <p className="text-sm mt-1 whitespace-pre-wrap" style={{color: '#F3F4F6'}}>{efir.incident_description}</p>
              </div>
            </CardContent>
          </Card>

          {/* Parties Involved */}
          <Card className="border" style={{backgroundColor: '#1F2937', borderColor: '#374151'}}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2" style={{color: '#F3F4F6'}}>
                <Users className="w-5 h-5" />
                Parties Involved
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium" style={{color: '#9CA3AF'}}>Complainant</label>
                  <p className="text-sm" style={{color: '#F3F4F6'}}>{efir.complainant_name || 'Not specified'}</p>
                  {efir.complainant_contact && (
                    <p className="text-xs" style={{color: '#9CA3AF'}}>{efir.complainant_contact}</p>
                  )}
                </div>
              </div>
              {efir.accused_details && (
                <div>
                  <label className="text-sm font-medium" style={{color: '#9CA3AF'}}>Accused Details</label>
                  <p className="text-sm mt-1 whitespace-pre-wrap" style={{color: '#F3F4F6'}}>{efir.accused_details}</p>
                </div>
              )}
              {efir.witness_details && (
                <div>
                  <label className="text-sm font-medium" style={{color: '#9CA3AF'}}>Witness Details</label>
                  <p className="text-sm mt-1 whitespace-pre-wrap" style={{color: '#F3F4F6'}}>{efir.witness_details}</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Case Information */}
          <Card className="border" style={{backgroundColor: '#1F2937', borderColor: '#374151'}}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2" style={{color: '#F3F4F6'}}>
                <Shield className="w-5 h-5" />
                Case Information
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium" style={{color: '#9CA3AF'}}>Case Details</label>
                <p className="text-sm mt-1 whitespace-pre-wrap" style={{color: '#F3F4F6'}}>{efir.case_details}</p>
              </div>
              {efir.evidence_details && (
                <div>
                  <label className="text-sm font-medium" style={{color: '#9CA3AF'}}>Evidence Details</label>
                  <p className="text-sm mt-1 whitespace-pre-wrap" style={{color: '#F3F4F6'}}>{efir.evidence_details}</p>
                </div>
              )}
              {efir.action_taken && (
                <div>
                  <label className="text-sm font-medium" style={{color: '#9CA3AF'}}>Action Taken</label>
                  <p className="text-sm mt-1 whitespace-pre-wrap" style={{color: '#F3F4F6'}}>{efir.action_taken}</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Related Information */}
          {(efir.related_tourist_id || efir.related_alert_id) && (
            <Card className="border" style={{backgroundColor: '#1F2937', borderColor: '#374151'}}>
              <CardHeader>
                <CardTitle className="flex items-center gap-2" style={{color: '#F3F4F6'}}>
                  <MapPin className="w-5 h-5" />
                  Related Information
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {efir.related_tourist_id && (
                    <div>
                      <label className="text-sm font-medium" style={{color: '#9CA3AF'}}>Related Tourist ID</label>
                      <p className="text-sm font-mono px-2 py-1 rounded" style={{backgroundColor: '#374151', color: '#F3F4F6'}}>{efir.related_tourist_id}</p>
                    </div>
                  )}
                  {efir.related_alert_id && (
                    <div>
                      <label className="text-sm font-medium" style={{color: '#9CA3AF'}}>Related Alert ID</label>
                      <p className="text-sm font-mono px-2 py-1 rounded" style={{backgroundColor: '#374151', color: '#F3F4F6'}}>{efir.related_alert_id}</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Digital Signatures */}
          {efir.signatures && efir.signatures.length > 0 && (
            <Card className="border" style={{backgroundColor: '#1F2937', borderColor: '#374151'}}>
              <CardHeader>
                <CardTitle className="flex items-center gap-2" style={{color: '#F3F4F6'}}>
                  <Signature className="w-5 h-5" />
                  Digital Signatures
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {efir.signatures.map((signature, index) => (
                    <div key={index} className="border rounded-lg p-4" style={{borderColor: '#16A34A', backgroundColor: '#15803D20'}}>
                      <div className="flex items-center gap-3 mb-2">
                        <CheckCircle className="w-5 h-5 text-green-600" />
                        <h4 className="font-medium text-green-400">{signature.officer_name}</h4>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                        <div>
                          <label className="font-medium" style={{color: '#9CA3AF'}}>Badge Number</label>
                          <p style={{color: '#F3F4F6'}}>{signature.officer_badge}</p>
                        </div>
                        <div>
                          <label className="font-medium" style={{color: '#9CA3AF'}}>Department</label>
                          <p style={{color: '#F3F4F6'}}>{signature.department}</p>
                        </div>
                        <div>
                          <label className="font-medium" style={{color: '#9CA3AF'}}>Signed At</label>
                          <p style={{color: '#F3F4F6'}}>{formatDate(signature.signed_at)}</p>
                        </div>
                        <div>
                          <label className="font-medium" style={{color: '#9CA3AF'}}>Signature Hash</label>
                          <p className="font-mono text-xs break-all" style={{color: '#F3F4F6'}}>{signature.signature_hash.substring(0, 32)}...</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* QR Code for Verification */}
          {efir.qr_code_data && (
            <Card className="border" style={{backgroundColor: '#1F2937', borderColor: '#374151'}}>
              <CardHeader>
                <CardTitle className="flex items-center gap-2" style={{color: '#F3F4F6'}}>
                  <QrCode className="w-5 h-5" />
                  Document Verification
                </CardTitle>
              </CardHeader>
              <CardContent className="text-center">
                <div className="inline-block p-4 rounded-lg border" style={{backgroundColor: '#F3F4F6', borderColor: '#374151'}}>
                  <QrCode className="w-32 h-32 mx-auto" style={{color: '#6B7280'}} />
                  <p className="text-sm mt-2" style={{color: '#6B7280'}}>Scan to verify document authenticity</p>
                </div>
                <p className="text-xs mt-4" style={{color: '#9CA3AF'}}>
                  QR Code contains verification data for this document
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default EFIRDetail;