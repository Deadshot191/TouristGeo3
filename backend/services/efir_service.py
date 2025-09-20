"""
E-FIR Service
Handles CRUD operations for Electronic First Information Reports
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

try:
    from ..models import (
        EFIRDocument, EFIRCreate, EFIRUpdate, EFIRResponse, 
        EFIRFilters, DocumentVersion, DigitalSignature
    )
    from ..database import get_database
    from .signature_service import SignatureService
    from .pdf_service import PDFService
except ImportError:
    from models import (
        EFIRDocument, EFIRCreate, EFIRUpdate, EFIRResponse, 
        EFIRFilters, DocumentVersion, DigitalSignature
    )
    from database import get_database
    from services.signature_service import SignatureService
    from services.pdf_service import PDFService


class EFIRService:
    def __init__(self):
        self.collection_name = "efir_documents"
        self.signature_service = SignatureService()
        self.pdf_service = PDFService()
    
    async def get_collection(self):
        """Get E-FIR documents collection"""
        db = await get_database()
        return db[self.collection_name]
    
    def generate_fir_number(self) -> str:
        """Generate unique FIR number"""
        year = datetime.utcnow().year
        # In production, this should be atomic and sequential
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"FIR-{year}-{unique_id}"
    
    async def create_efir(self, efir_data: EFIRCreate, created_by: str) -> EFIRDocument:
        """Create new E-FIR document"""
        collection = await self.get_collection()
        
        # Generate FIR number
        fir_number = self.generate_fir_number()
        
        # Create document
        efir_doc = EFIRDocument(
            fir_number=fir_number,
            title=efir_data.title,
            fir_type=efir_data.fir_type,
            priority=efir_data.priority,
            incident_date=efir_data.incident_date,
            incident_location=efir_data.incident_location,
            incident_description=efir_data.incident_description,
            related_tourist_id=efir_data.related_tourist_id,
            related_alert_id=efir_data.related_alert_id,
            complainant_name=efir_data.complainant_name,
            complainant_contact=efir_data.complainant_contact,
            accused_details=efir_data.accused_details,
            witness_details=efir_data.witness_details,
            case_details=efir_data.case_details,
            evidence_details=efir_data.evidence_details,
            action_taken=efir_data.action_taken,
            created_by=created_by
        )
        
        # Calculate initial document hash
        efir_doc.document_hash = self.signature_service.calculate_document_hash(efir_doc)
        
        # Insert document
        result = await collection.insert_one(efir_doc.model_dump(by_alias=True))
        efir_doc.id = result.inserted_id
        
        return efir_doc
    
    async def get_efir_by_id(self, efir_id: str) -> Optional[EFIRDocument]:
        """Get E-FIR document by ID"""
        collection = await self.get_collection()
        
        doc = await collection.find_one({"_id": ObjectId(efir_id)})
        if doc:
            return EFIRDocument(**doc)
        return None
    
    async def get_efir_by_number(self, fir_number: str) -> Optional[EFIRDocument]:
        """Get E-FIR document by FIR number"""
        collection = await self.get_collection()
        
        doc = await collection.find_one({"fir_number": fir_number})
        if doc:
            return EFIRDocument(**doc)
        return None
    
    async def update_efir(self, efir_id: str, update_data: EFIRUpdate, modified_by: str) -> Optional[EFIRDocument]:
        """Update E-FIR document with versioning"""
        collection = await self.get_collection()
        
        # Get current document
        current_doc = await self.get_efir_by_id(efir_id)
        if not current_doc:
            return None
        
        # Create version entry for current state
        version_entry = DocumentVersion(
            version_number=current_doc.current_version,
            modified_by=modified_by,
            changes_summary=update_data.changes_summary,
            document_hash=current_doc.document_hash
        )
        
        # Update document
        update_dict = update_data.model_dump(exclude_unset=True, exclude={"changes_summary"})
        update_dict["current_version"] = current_doc.current_version + 1
        
        # Calculate new document hash
        temp_doc = current_doc.model_copy(update=update_dict)
        temp_doc.current_version = current_doc.current_version + 1
        update_dict["document_hash"] = self.signature_service.calculate_document_hash(temp_doc)
        
        # Perform update
        result = await collection.update_one(
            {"_id": ObjectId(efir_id)},
            {"$set": update_dict, "$push": {"versions": version_entry.model_dump()}}
        )
        
        if result.modified_count > 0:
            return await self.get_efir_by_id(efir_id)
        return None
    
    async def delete_efir(self, efir_id: str) -> bool:
        """Delete E-FIR document"""
        collection = await self.get_collection()
        
        # Get document first to delete associated PDF
        efir_doc = await self.get_efir_by_id(efir_id)
        if efir_doc and efir_doc.pdf_file_path:
            self.pdf_service.delete_pdf(efir_doc.pdf_file_path)
        
        result = await collection.delete_one({"_id": ObjectId(efir_id)})
        return result.deleted_count > 0
    
    async def list_efirs(self, filters: EFIRFilters) -> List[EFIRResponse]:
        """List E-FIR documents with filtering"""
        collection = await self.get_collection()
        
        # Build query
        query = {}
        
        if filters.fir_type:
            query["fir_type"] = filters.fir_type.value
        
        if filters.status:
            query["status"] = filters.status.value
        
        if filters.priority:
            query["priority"] = filters.priority.value
        
        if filters.created_by:
            query["created_by"] = filters.created_by
        
        if filters.start_date or filters.end_date:
            date_query = {}
            if filters.start_date:
                date_query["$gte"] = filters.start_date
            if filters.end_date:
                date_query["$lte"] = filters.end_date
            query["created_at"] = date_query
        
        if filters.search:
            query["$or"] = [
                {"title": {"$regex": filters.search, "$options": "i"}},
                {"fir_number": {"$regex": filters.search, "$options": "i"}},
                {"incident_description": {"$regex": filters.search, "$options": "i"}},
                {"case_details": {"$regex": filters.search, "$options": "i"}}
            ]
        
        # Execute query
        cursor = collection.find(query).sort("created_at", -1).skip(filters.skip).limit(filters.limit)
        docs = await cursor.to_list(length=filters.limit)
        
        # Convert to response models
        responses = []
        for doc in docs:
            efir_doc = EFIRDocument(**doc)
            response = EFIRResponse(
                id=str(efir_doc.id),
                fir_number=efir_doc.fir_number,
                title=efir_doc.title,
                fir_type=efir_doc.fir_type,
                priority=efir_doc.priority,
                status=efir_doc.status,
                incident_date=efir_doc.incident_date,
                incident_location=efir_doc.incident_location,
                incident_description=efir_doc.incident_description,
                related_tourist_id=efir_doc.related_tourist_id,
                related_alert_id=efir_doc.related_alert_id,
                complainant_name=efir_doc.complainant_name,
                complainant_contact=efir_doc.complainant_contact,
                accused_details=efir_doc.accused_details,
                witness_details=efir_doc.witness_details,
                case_details=efir_doc.case_details,
                evidence_details=efir_doc.evidence_details,
                action_taken=efir_doc.action_taken,
                created_by=efir_doc.created_by,
                created_at=efir_doc.created_at,
                current_version=efir_doc.current_version,
                signatures=efir_doc.signatures,
                qr_code_data=efir_doc.qr_code_data,
                has_pdf=bool(efir_doc.pdf_file_path)
            )
            responses.append(response)
        
        return responses
    
    async def sign_efir(self, efir_id: str, officer_id: str, officer_data: Dict[str, Any]) -> bool:
        """Add digital signature to E-FIR document"""
        collection = await self.get_collection()
        
        # Get document
        efir_doc = await self.get_efir_by_id(efir_id)
        if not efir_doc:
            return False
        
        # Check if officer already signed
        for sig in efir_doc.signatures:
            if sig.officer_id == officer_id:
                raise ValueError("Officer has already signed this document")
        
        # Create digital signature
        signature = self.signature_service.sign_document(efir_doc, officer_id, officer_data)
        
        # Add signature to document
        result = await collection.update_one(
            {"_id": ObjectId(efir_id)},
            {"$push": {"signatures": signature.model_dump()}}
        )
        
        return result.modified_count > 0
    
    async def generate_pdf(self, efir_id: str, verification_url: str = None) -> Optional[str]:
        """Generate PDF for E-FIR document"""
        efir_doc = await self.get_efir_by_id(efir_id)
        if not efir_doc:
            return None
        
        try:
            # Generate PDF
            pdf_path = self.pdf_service.generate_pdf(efir_doc, verification_url)
            
            # Update document with PDF path
            collection = await self.get_collection()
            await collection.update_one(
                {"_id": ObjectId(efir_id)},
                {"$set": {"pdf_file_path": pdf_path}}
            )
            
            return pdf_path
        except Exception as e:
            print(f"PDF generation failed: {e}")
            return None
    
    async def verify_document(self, fir_number: str, document_hash: str) -> Dict[str, Any]:
        """Verify document authenticity using QR code data"""
        efir_doc = await self.get_efir_by_number(fir_number)
        if not efir_doc:
            return {"valid": False, "error": "Document not found"}
        
        # Verify document hash
        current_hash = self.signature_service.calculate_document_hash(efir_doc)
        if current_hash != document_hash:
            return {"valid": False, "error": "Document has been modified"}
        
        # Verify signatures
        signature_results = self.signature_service.verify_all_signatures(efir_doc)
        
        return {
            "valid": True,
            "fir_number": efir_doc.fir_number,
            "title": efir_doc.title,
            "status": efir_doc.status.value,
            "created_at": efir_doc.created_at.isoformat(),
            "version": efir_doc.current_version,
            "signatures_count": len(efir_doc.signatures),
            "signature_verifications": signature_results
        }
    
    async def get_document_history(self, efir_id: str) -> List[Dict[str, Any]]:
        """Get version history of document"""
        efir_doc = await self.get_efir_by_id(efir_id)
        if not efir_doc:
            return []
        
        history = []
        
        # Add current version
        history.append({
            "version": efir_doc.current_version,
            "modified_by": "Current",
            "modified_at": efir_doc.created_at.isoformat(),
            "changes_summary": "Current version",
            "document_hash": efir_doc.document_hash
        })
        
        # Add previous versions
        for version in reversed(efir_doc.versions):
            history.append({
                "version": version.version_number,
                "modified_by": version.modified_by,
                "modified_at": version.modified_at.isoformat(),
                "changes_summary": version.changes_summary,
                "document_hash": version.document_hash
            })
        
        return sorted(history, key=lambda x: x["version"], reverse=True)