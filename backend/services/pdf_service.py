"""
PDF Generation Service for E-FIR Documents
Generates professional PDF documents from E-FIR data
"""

import os
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import qrcode
from io import BytesIO
import base64

try:
    from ..models import EFIRDocument, DigitalSignature
except ImportError:
    from models import EFIRDocument, DigitalSignature


class PDFService:
    def __init__(self):
        self.pdf_storage_path = Path("/app/storage/pdfs")
        self.pdf_storage_path.mkdir(parents=True, exist_ok=True)
        
        # Font configuration for better PDF rendering
        self.font_config = FontConfiguration()
        
        # CSS styles for professional PDF layout
        self.pdf_styles = """
        @page {
            size: A4;
            margin: 2cm;
            @top-center {
                content: "E-FIR Document - " attr(title);
                font-size: 10pt;
                color: #666;
            }
            @bottom-center {
                content: "Page " counter(page) " of " counter(pages);
                font-size: 10pt;
                color: #666;
            }
        }
        
        body {
            font-family: 'DejaVu Sans', Arial, sans-serif;
            font-size: 11pt;
            line-height: 1.4;
            color: #333;
        }
        
        .header {
            text-align: center;
            border-bottom: 2px solid #2563eb;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        
        .logo {
            font-size: 24pt;
            font-weight: bold;
            color: #2563eb;
            margin-bottom: 10px;
        }
        
        .fir-number {
            font-size: 18pt;
            font-weight: bold;
            color: #dc2626;
            margin: 10px 0;
        }
        
        .section {
            margin-bottom: 25px;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 20px;
        }
        
        .section-title {
            font-size: 14pt;
            font-weight: bold;
            color: #1f2937;
            margin-bottom: 15px;
            border-bottom: 1px solid #d1d5db;
            padding-bottom: 5px;
        }
        
        .field-group {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 15px;
        }
        
        .field {
            flex: 1;
            min-width: 200px;
        }
        
        .field-label {
            font-weight: bold;
            color: #374151;
            margin-bottom: 5px;
        }
        
        .field-value {
            color: #111827;
            padding: 8px;
            background-color: #f9fafb;
            border-radius: 4px;
            border: 1px solid #e5e7eb;
        }
        
        .priority-high { color: #dc2626; font-weight: bold; }
        .priority-urgent { color: #991b1b; font-weight: bold; background-color: #fee2e2; }
        .priority-medium { color: #d97706; font-weight: bold; }
        .priority-low { color: #059669; }
        
        .status-draft { color: #6b7280; }
        .status-submitted { color: #2563eb; }
        .status-under-investigation { color: #d97706; }
        .status-closed { color: #059669; }
        
        .signatures-section {
            margin-top: 40px;
            border-top: 2px solid #2563eb;
            padding-top: 20px;
        }
        
        .signature-block {
            display: inline-block;
            width: 45%;
            margin: 10px 2.5%;
            padding: 15px;
            border: 1px solid #d1d5db;
            border-radius: 8px;
        }
        
        .qr-code {
            text-align: center;
            margin: 20px 0;
        }
        
        .watermark {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) rotate(-45deg);
            font-size: 72pt;
            color: rgba(0, 0, 0, 0.05);
            z-index: -1;
            pointer-events: none;
        }
        
        @media print {
            .no-print { display: none; }
        }
        """

    def generate_qr_code(self, data: str) -> str:
        """Generate QR code as base64 encoded image"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode()

    def create_html_template(self, efir_doc: EFIRDocument, verification_url: str = None) -> str:
        """Create HTML template for E-FIR document"""
        
        # Generate QR code for verification
        qr_data = f"FIR:{efir_doc.fir_number}|Hash:{efir_doc.document_hash}|Version:{efir_doc.current_version}"
        if verification_url:
            qr_data = f"{verification_url}?fir={efir_doc.fir_number}&hash={efir_doc.document_hash}"
        
        qr_code_base64 = self.generate_qr_code(qr_data)
        
        # Format signatures
        signatures_html = ""
        for sig in efir_doc.signatures:
            signatures_html += f"""
            <div class="signature-block">
                <div class="field-label">Digital Signature</div>
                <div class="field-value">
                    <strong>{sig.officer_name}</strong><br>
                    Badge: {sig.officer_badge}<br>
                    Department: {sig.department}<br>
                    Signed: {sig.signed_at.strftime('%Y-%m-%d %H:%M:%S')} UTC
                </div>
            </div>
            """
        
        # Format location
        location_str = f"Lat: {efir_doc.incident_location.coordinates.coordinates[1]:.6f}, Lng: {efir_doc.incident_location.coordinates.coordinates[0]:.6f}"
        if efir_doc.incident_location.address:
            location_str += f"<br>{efir_doc.incident_location.address}"

        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>E-FIR Document - {efir_doc.fir_number}</title>
            <style>{self.pdf_styles}</style>
        </head>
        <body>
            <div class="watermark">E-FIR OFFICIAL</div>
            
            <div class="header">
                <div class="logo">🛡️ ELECTRONIC FIRST INFORMATION REPORT</div>
                <div class="fir-number">{efir_doc.fir_number}</div>
                <div>Generated on: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</div>
            </div>

            <div class="section">
                <div class="section-title">📋 CASE INFORMATION</div>
                <div class="field-group">
                    <div class="field">
                        <div class="field-label">Case Title</div>
                        <div class="field-value">{efir_doc.title}</div>
                    </div>
                    <div class="field">
                        <div class="field-label">FIR Type</div>
                        <div class="field-value">{efir_doc.fir_type.value.replace('_', ' ').title()}</div>
                    </div>
                </div>
                <div class="field-group">
                    <div class="field">
                        <div class="field-label">Priority</div>
                        <div class="field-value priority-{efir_doc.priority.value}">{efir_doc.priority.value.upper()}</div>
                    </div>
                    <div class="field">
                        <div class="field-label">Status</div>
                        <div class="field-value status-{efir_doc.status.value.replace('_', '-')}">{efir_doc.status.value.replace('_', ' ').title()}</div>
                    </div>
                </div>
                <div class="field-group">
                    <div class="field">
                        <div class="field-label">Document Version</div>
                        <div class="field-value">Version {efir_doc.current_version}</div>
                    </div>
                    <div class="field">
                        <div class="field-label">Created By</div>
                        <div class="field-value">{efir_doc.created_by}</div>
                    </div>
                </div>
            </div>

            <div class="section">
                <div class="section-title">📍 INCIDENT DETAILS</div>
                <div class="field-group">
                    <div class="field">
                        <div class="field-label">Incident Date & Time</div>
                        <div class="field-value">{efir_doc.incident_date.strftime('%Y-%m-%d %H:%M:%S')} UTC</div>
                    </div>
                    <div class="field">
                        <div class="field-label">Location</div>
                        <div class="field-value">{location_str}</div>
                    </div>
                </div>
                <div class="field">
                    <div class="field-label">Incident Description</div>
                    <div class="field-value">{efir_doc.incident_description}</div>
                </div>
            </div>

            <div class="section">
                <div class="section-title">👥 PARTIES INVOLVED</div>
                <div class="field-group">
                    <div class="field">
                        <div class="field-label">Complainant Name</div>
                        <div class="field-value">{efir_doc.complainant_name or 'Not specified'}</div>
                    </div>
                    <div class="field">
                        <div class="field-label">Complainant Contact</div>
                        <div class="field-value">{efir_doc.complainant_contact or 'Not specified'}</div>
                    </div>
                </div>
                <div class="field">
                    <div class="field-label">Accused Details</div>
                    <div class="field-value">{efir_doc.accused_details or 'Not specified'}</div>
                </div>
                <div class="field">
                    <div class="field-label">Witness Details</div>
                    <div class="field-value">{efir_doc.witness_details or 'Not specified'}</div>
                </div>
            </div>

            <div class="section">
                <div class="section-title">⚖️ CASE DETAILS</div>
                <div class="field">
                    <div class="field-label">Case Details</div>
                    <div class="field-value">{efir_doc.case_details}</div>
                </div>
                {f'<div class="field"><div class="field-label">Evidence Details</div><div class="field-value">{efir_doc.evidence_details}</div></div>' if efir_doc.evidence_details else ''}
                {f'<div class="field"><div class="field-label">Action Taken</div><div class="field-value">{efir_doc.action_taken}</div></div>' if efir_doc.action_taken else ''}
            </div>

            {f'''
            <div class="section">
                <div class="section-title">🔗 RELATED INFORMATION</div>
                {f'<div class="field"><div class="field-label">Related Tourist ID</div><div class="field-value">{efir_doc.related_tourist_id}</div></div>' if efir_doc.related_tourist_id else ''}
                {f'<div class="field"><div class="field-label">Related Alert ID</div><div class="field-value">{efir_doc.related_alert_id}</div></div>' if efir_doc.related_alert_id else ''}
            </div>
            ''' if efir_doc.related_tourist_id or efir_doc.related_alert_id else ''}

            <div class="qr-code">
                <div class="field-label">Document Verification QR Code</div>
                <img src="data:image/png;base64,{qr_code_base64}" alt="Verification QR Code" style="width: 150px; height: 150px;">
                <br>
                <small>Scan to verify document authenticity</small>
            </div>

            {f'''
            <div class="signatures-section">
                <div class="section-title">✍️ DIGITAL SIGNATURES</div>
                {signatures_html}
            </div>
            ''' if signatures_html else ''}

            <div class="section" style="margin-top: 40px; text-align: center; color: #6b7280; font-size: 10pt;">
                <div>Document Hash: {efir_doc.document_hash}</div>
                <div>This is a digitally generated E-FIR document. No physical signature required.</div>
            </div>
        </body>
        </html>
        """
        
        return html_template

    def generate_pdf(self, efir_doc: EFIRDocument, verification_url: str = None) -> str:
        """
        Generate PDF from E-FIR document
        Returns path to generated PDF file
        """
        try:
            # Create HTML content
            html_content = self.create_html_template(efir_doc, verification_url)
            
            # Generate filename
            safe_fir_number = efir_doc.fir_number.replace('/', '-').replace(' ', '_')
            filename = f"{safe_fir_number}_v{efir_doc.current_version}.pdf"
            pdf_path = self.pdf_storage_path / filename
            
            # Generate PDF
            html_doc = HTML(string=html_content)
            css_doc = CSS(string=self.pdf_styles, font_config=self.font_config)
            
            html_doc.write_pdf(
                str(pdf_path),
                stylesheets=[css_doc],
                font_config=self.font_config
            )
            
            return str(pdf_path)
            
        except Exception as e:
            raise Exception(f"PDF generation failed: {str(e)}")

    def get_pdf_path(self, fir_number: str, version: int = None) -> Optional[str]:
        """Get path to existing PDF file"""
        safe_fir_number = fir_number.replace('/', '-').replace(' ', '_')
        
        if version:
            filename = f"{safe_fir_number}_v{version}.pdf"
        else:
            # Find latest version
            matching_files = list(self.pdf_storage_path.glob(f"{safe_fir_number}_v*.pdf"))
            if not matching_files:
                return None
            filename = max(matching_files).name
        
        pdf_path = self.pdf_storage_path / filename
        return str(pdf_path) if pdf_path.exists() else None

    def delete_pdf(self, pdf_path: str) -> bool:
        """Delete PDF file"""
        try:
            Path(pdf_path).unlink()
            return True
        except Exception:
            return False