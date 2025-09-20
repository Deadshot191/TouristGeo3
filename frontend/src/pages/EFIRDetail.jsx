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
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">Loading E-FIR document...</span>
      </div>
    );
  }

  if (!efir) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <Card>
          <CardContent className="text-center py-12">
            <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">E-FIR Document Not Found</h3>
            <p className="text-gray-600 mb-4">The requested E-FIR document could not be found.</p>
            <Button onClick={() => navigate('/efir')}>
              Back to E-FIR Documents
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

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
        
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            <FileText className="w-8 h-8 text-blue-600" />
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{efir.fir_number}</h1>
              <p className="text-lg text-gray-600">{efir.title}</p>
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
            >
              <Edit className="w-4 h-4 mr-2" />
              Edit
            </Button>
            <Button
              onClick={handleDownloadPDF}
              variant="outline"
              size="sm"
            >
              <Download className="w-4 h-4 mr-2" />
              Download PDF
            </Button>
            {!efir.has_pdf && (
              <Button
                onClick={handleGeneratePDF}
                variant="outline"
                size="sm"
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
                >
                  <Signature className="w-4 h-4 mr-2" />
                  {isAlreadySigned ? 'Already Signed' : 'Sign Document'}
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Digital Signature</DialogTitle>
                </DialogHeader>
                <div className="space-y-4">
                  <p className="text-sm text-gray-600">
                    Enter your password to digitally sign this E-FIR document.
                  </p>
                  <div>
                    <label className="text-sm font-medium text-gray-700 mb-1 block">
                      Password
                    </label>
                    <Input
                      type="password"
                      value={signPassword}
                      onChange={(e) => setSignPassword(e.target.value)}
                      placeholder="Enter your password"
                    />
                  </div>
                  <div className="flex justify-end gap-2">
                    <Button
                      variant="outline"
                      onClick={() => {
                        setShowSignDialog(false);
                        setSignPassword('');
                      }}
                    >
                      Cancel
                    </Button>
                    <Button
                      onClick={handleSignDocument}
                      disabled={signing || !signPassword.trim()}
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
            >
              <Clock className="w-4 h-4 mr-2" />
              History
            </Button>
          </div>
        </div>
      </div>

      <div className="grid gap-6">
        {/* Document Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5" />
              Document Information
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-500">FIR Number</label>
                <p className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">{efir.fir_number}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">Type</label>
                <p className="text-sm">{getTypeLabel(efir.fir_type)}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">Version</label>
                <p className="text-sm">{efir.current_version}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">Created By</label>
                <p className="text-sm">{efir.created_by}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">Created Date</label>
                <p className="text-sm">{formatDate(efir.created_at)}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">PDF Status</label>
                <p className="text-sm">{efir.has_pdf ? 'Generated' : 'Not Generated'}</p>
              </div>
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
                <label className="text-sm font-medium text-gray-500">Incident Date</label>
                <p className="text-sm">{formatDate(efir.incident_date)}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">Location</label>
                <p className="text-sm">
                  {efir.incident_location?.address || 'No address provided'}
                  {efir.incident_location?.coordinates && (
                    <span className="block text-xs text-gray-400 font-mono">
                      {efir.incident_location.coordinates.coordinates[1].toFixed(6)}, 
                      {efir.incident_location.coordinates.coordinates[0].toFixed(6)}
                    </span>
                  )}
                </p>
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Description</label>
              <p className="text-sm mt-1 whitespace-pre-wrap">{efir.incident_description}</p>
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
                <label className="text-sm font-medium text-gray-500">Complainant</label>
                <p className="text-sm">{efir.complainant_name || 'Not specified'}</p>
                {efir.complainant_contact && (
                  <p className="text-xs text-gray-400">{efir.complainant_contact}</p>
                )}
              </div>
            </div>
            {efir.accused_details && (
              <div>
                <label className="text-sm font-medium text-gray-500">Accused Details</label>
                <p className="text-sm mt-1 whitespace-pre-wrap">{efir.accused_details}</p>
              </div>
            )}
            {efir.witness_details && (
              <div>
                <label className="text-sm font-medium text-gray-500">Witness Details</label>
                <p className="text-sm mt-1 whitespace-pre-wrap">{efir.witness_details}</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Case Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="w-5 h-5" />
              Case Information
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-500">Case Details</label>
              <p className="text-sm mt-1 whitespace-pre-wrap">{efir.case_details}</p>
            </div>
            {efir.evidence_details && (
              <div>
                <label className="text-sm font-medium text-gray-500">Evidence Details</label>
                <p className="text-sm mt-1 whitespace-pre-wrap">{efir.evidence_details}</p>
              </div>
            )}
            {efir.action_taken && (
              <div>
                <label className="text-sm font-medium text-gray-500">Action Taken</label>
                <p className="text-sm mt-1 whitespace-pre-wrap">{efir.action_taken}</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Related Information */}
        {(efir.related_tourist_id || efir.related_alert_id) && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MapPin className="w-5 h-5" />
                Related Information
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {efir.related_tourist_id && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">Related Tourist ID</label>
                    <p className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">{efir.related_tourist_id}</p>
                  </div>
                )}
                {efir.related_alert_id && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">Related Alert ID</label>
                    <p className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">{efir.related_alert_id}</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Digital Signatures */}
        {efir.signatures && efir.signatures.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Signature className="w-5 h-5" />
                Digital Signatures
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {efir.signatures.map((signature, index) => (
                  <div key={index} className="border rounded-lg p-4 bg-green-50">
                    <div className="flex items-center gap-3 mb-2">
                      <CheckCircle className="w-5 h-5 text-green-600" />
                      <h4 className="font-medium text-green-900">{signature.officer_name}</h4>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      <div>
                        <label className="font-medium text-gray-500">Badge Number</label>
                        <p>{signature.officer_badge}</p>
                      </div>
                      <div>
                        <label className="font-medium text-gray-500">Department</label>
                        <p>{signature.department}</p>
                      </div>
                      <div>
                        <label className="font-medium text-gray-500">Signed At</label>
                        <p>{formatDate(signature.signed_at)}</p>
                      </div>
                      <div>
                        <label className="font-medium text-gray-500">Signature Hash</label>
                        <p className="font-mono text-xs break-all">{signature.signature_hash.substring(0, 32)}...</p>
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
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <QrCode className="w-5 h-5" />
                Document Verification
              </CardTitle>
            </CardHeader>
            <CardContent className="text-center">
              <div className="bg-white inline-block p-4 rounded-lg border">
                <QrCode className="w-32 h-32 text-gray-400 mx-auto" />
                <p className="text-sm text-gray-600 mt-2">Scan to verify document authenticity</p>
              </div>
              <p className="text-xs text-gray-500 mt-4">
                QR Code contains verification data for this document
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default EFIRDetail;