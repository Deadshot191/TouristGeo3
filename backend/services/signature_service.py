"""
Digital Signature Service for E-FIR Documents
Handles digital signing and verification of documents
"""

import hashlib
import base64
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from pathlib import Path
import json
import os

try:
    from ..models import DigitalSignature, EFIRDocument
    from ..auth import get_current_user
except ImportError:
    from models import DigitalSignature, EFIRDocument
    from auth import get_current_user


class SignatureService:
    def __init__(self):
        self.keys_storage_path = Path("/app/storage/keys")
        self.keys_storage_path.mkdir(parents=True, exist_ok=True)
        
    def generate_key_pair(self, officer_id: str) -> Tuple[str, str]:
        """
        Generate RSA key pair for an officer
        Returns (private_key_pem, public_key_pem)
        """
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Get public key
        public_key = private_key.public_key()
        
        # Serialize keys to PEM format
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
        # Store keys
        self._store_officer_keys(officer_id, private_pem, public_pem)
        
        return private_pem, public_pem
    
    def _store_officer_keys(self, officer_id: str, private_key: str, public_key: str):
        """Store officer's key pair securely"""
        officer_key_dir = self.keys_storage_path / officer_id
        officer_key_dir.mkdir(exist_ok=True)
        
        # Store private key (in production, this should be encrypted)
        private_key_path = officer_key_dir / "private_key.pem"
        with open(private_key_path, 'w') as f:
            f.write(private_key)
        
        # Store public key
        public_key_path = officer_key_dir / "public_key.pem"
        with open(public_key_path, 'w') as f:
            f.write(public_key)
        
        # Set restrictive permissions
        os.chmod(private_key_path, 0o600)
        os.chmod(public_key_path, 0o644)
    
    def get_officer_keys(self, officer_id: str) -> Tuple[Optional[str], Optional[str]]:
        """Get officer's key pair"""
        officer_key_dir = self.keys_storage_path / officer_id
        
        private_key_path = officer_key_dir / "private_key.pem"
        public_key_path = officer_key_dir / "public_key.pem"
        
        private_key = None
        public_key = None
        
        if private_key_path.exists():
            with open(private_key_path, 'r') as f:
                private_key = f.read()
        
        if public_key_path.exists():
            with open(public_key_path, 'r') as f:
                public_key = f.read()
        
        return private_key, public_key
    
    def calculate_document_hash(self, efir_doc: EFIRDocument) -> str:
        """Calculate SHA-256 hash of document content for signing"""
        # Create a canonical representation of the document for hashing
        doc_data = {
            "fir_number": efir_doc.fir_number,
            "title": efir_doc.title,
            "fir_type": efir_doc.fir_type.value,
            "priority": efir_doc.priority.value,
            "incident_date": efir_doc.incident_date.isoformat(),
            "incident_location": {
                "coordinates": efir_doc.incident_location.coordinates.coordinates,
                "address": efir_doc.incident_location.address
            },
            "incident_description": efir_doc.incident_description,
            "case_details": efir_doc.case_details,
            "complainant_name": efir_doc.complainant_name,
            "complainant_contact": efir_doc.complainant_contact,
            "accused_details": efir_doc.accused_details,
            "witness_details": efir_doc.witness_details,
            "evidence_details": efir_doc.evidence_details,
            "action_taken": efir_doc.action_taken,
            "version": efir_doc.current_version
        }
        
        # Convert to JSON string and calculate hash
        doc_json = json.dumps(doc_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(doc_json.encode('utf-8')).hexdigest()
    
    def sign_document(self, efir_doc: EFIRDocument, officer_id: str, officer_data: Dict[str, Any], password: str = None) -> DigitalSignature:
        """
        Digitally sign an E-FIR document
        """
        # Get officer's private key
        private_key_pem, public_key_pem = self.get_officer_keys(officer_id)
        
        if not private_key_pem:
            # Generate keys if they don't exist
            private_key_pem, public_key_pem = self.generate_key_pair(officer_id)
        
        # Load private key
        private_key = load_pem_private_key(
            private_key_pem.encode('utf-8'),
            password=None,  # In production, use password-protected keys
        )
        
        # Calculate document hash
        document_hash = self.calculate_document_hash(efir_doc)
        
        # Sign the document hash
        signature = private_key.sign(
            document_hash.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        # Encode signature as base64
        signature_b64 = base64.b64encode(signature).decode('utf-8')
        
        # Create digital signature object
        digital_sig = DigitalSignature(
            officer_id=officer_id,
            officer_name=officer_data.get('full_name', 'Unknown Officer'),
            officer_badge=officer_data.get('badge_number', 'N/A'),
            department=officer_data.get('department', 'Unknown Department'),
            signature_hash=signature_b64,
            verification_key=public_key_pem
        )
        
        return digital_sig
    
    def verify_signature(self, efir_doc: EFIRDocument, signature: DigitalSignature) -> bool:
        """
        Verify a digital signature
        """
        try:
            # Load public key
            public_key = load_pem_public_key(signature.verification_key.encode('utf-8'))
            
            # Calculate current document hash
            document_hash = self.calculate_document_hash(efir_doc)
            
            # Decode signature
            signature_bytes = base64.b64decode(signature.signature_hash)
            
            # Verify signature
            public_key.verify(
                signature_bytes,
                document_hash.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return True
        except Exception as e:
            print(f"Signature verification failed: {e}")
            return False
    
    def verify_all_signatures(self, efir_doc: EFIRDocument) -> Dict[str, bool]:
        """
        Verify all signatures on a document
        Returns dict with signature verification results
        """
        results = {}
        
        for i, signature in enumerate(efir_doc.signatures):
            signature_id = f"{signature.officer_id}_{signature.signed_at.isoformat()}"
            results[signature_id] = self.verify_signature(efir_doc, signature)
        
        return results
    
    def get_signature_info(self, signature: DigitalSignature) -> Dict[str, Any]:
        """Get human-readable signature information"""
        return {
            "officer_name": signature.officer_name,
            "officer_badge": signature.officer_badge,
            "department": signature.department,
            "signed_at": signature.signed_at.isoformat(),
            "signature_hash": signature.signature_hash[:32] + "...",  # Truncated for display
        }
    
    def can_officer_sign(self, officer_id: str, officer_role: str) -> bool:
        """Check if officer has permission to sign documents"""
        # In a real system, this would check officer's permissions
        # For now, allow police and tourism_admin roles
        allowed_roles = ["police", "tourism_admin"]
        return officer_role in allowed_roles
    
    def remove_officer_keys(self, officer_id: str) -> bool:
        """Remove officer's key pair (for key rotation or officer removal)"""
        try:
            officer_key_dir = self.keys_storage_path / officer_id
            if officer_key_dir.exists():
                for key_file in officer_key_dir.glob("*.pem"):
                    key_file.unlink()
                officer_key_dir.rmdir()
            return True
        except Exception:
            return False