import hashlib
import json
from datetime import datetime
from typing import Optional, Dict, Any
from ..database import get_database
from ..models import DataAccessLog
import logging

logger = logging.getLogger(__name__)

class BlockchainSimulator:
    """
    Simulates blockchain functionality for immutable audit logging
    Creates a chain of audit log entries with cryptographic hashes
    """
    
    async def get_last_log_entry(self) -> Optional[Dict[Any, Any]]:
        """Get the most recent log entry for chain linking"""
        try:
            db = get_database()
            last_entry = await db.data_access_log.find_one(
                {},
                sort=[("block_number", -1)]
            )
            return last_entry
        except Exception as e:
            logger.error(f"Error getting last log entry: {e}")
            return None
    
    async def get_next_block_number(self) -> int:
        """Get the next block number in sequence"""
        last_entry = await self.get_last_log_entry()
        if last_entry:
            return last_entry.get("block_number", 0) + 1
        return 1
    
    def calculate_log_hash(self, log_entry: Dict[Any, Any]) -> str:
        """
        Calculate cryptographic hash of a log entry
        Creates a deterministic hash based on entry content
        """
        # Create a consistent string representation for hashing
        hash_data = {
            "tourist_id": log_entry.get("tourist_id"),
            "authority_id": log_entry.get("authority_id"),
            "access_type": log_entry.get("access_type"),
            "access_reason": log_entry.get("access_reason"),
            "timestamp": log_entry.get("timestamp").isoformat() if log_entry.get("timestamp") else None,
            "block_number": log_entry.get("block_number"),
            "previous_log_hash": log_entry.get("previous_log_hash")
        }
        
        # Convert to JSON string with sorted keys for consistency
        hash_string = json.dumps(hash_data, sort_keys=True, default=str)
        
        # Calculate SHA-256 hash
        return hashlib.sha256(hash_string.encode('utf-8')).hexdigest()
    
    async def create_immutable_log_entry(self, log_data: Dict[Any, Any]) -> DataAccessLog:
        """
        Create a new immutable log entry in the blockchain simulation
        Links to previous entry and calculates cryptographic hash
        """
        try:
            # Get the previous log entry for chain linking
            last_entry = await self.get_last_log_entry()
            previous_hash = last_entry.get("current_log_hash") if last_entry else None
            
            # Get next block number
            block_number = await self.get_next_block_number()
            
            # Create the log entry with blockchain simulation fields
            log_entry_data = {
                **log_data,
                "previous_log_hash": previous_hash,
                "block_number": block_number,
                "verification_timestamp": datetime.utcnow()
            }
            
            # Calculate hash for this entry
            current_hash = self.calculate_log_hash(log_entry_data)
            log_entry_data["current_log_hash"] = current_hash
            
            # Create and return the log entry
            log_entry = DataAccessLog(**log_entry_data)
            
            logger.info(f"Created immutable log entry - Block: {block_number}, Hash: {current_hash[:16]}...")
            
            return log_entry
            
        except Exception as e:
            logger.error(f"Error creating immutable log entry: {e}")
            raise
    
    async def verify_chain_integrity(self, limit: int = 100) -> Dict[str, Any]:
        """
        Verify the integrity of the blockchain simulation chain
        Checks that all hash links are valid
        """
        try:
            db = get_database()
            
            # Get recent log entries
            entries = await db.data_access_log.find({}).sort("block_number", 1).limit(limit).to_list(length=limit)
            
            if not entries:
                return {"status": "valid", "message": "No entries to verify", "verified_count": 0}
            
            verified_count = 0
            broken_links = []
            
            for i, entry in enumerate(entries):
                # Verify hash calculation
                expected_hash = self.calculate_log_hash(entry)
                if entry.get("current_log_hash") != expected_hash:
                    broken_links.append({
                        "block_number": entry.get("block_number"),
                        "error": "Hash mismatch",
                        "expected": expected_hash,
                        "actual": entry.get("current_log_hash")
                    })
                    continue
                
                # Verify chain link (except for first entry)
                if i > 0:
                    previous_entry = entries[i-1]
                    expected_previous_hash = previous_entry.get("current_log_hash")
                    actual_previous_hash = entry.get("previous_log_hash")
                    
                    if expected_previous_hash != actual_previous_hash:
                        broken_links.append({
                            "block_number": entry.get("block_number"),
                            "error": "Chain link broken",
                            "expected_previous": expected_previous_hash,
                            "actual_previous": actual_previous_hash
                        })
                        continue
                
                verified_count += 1
            
            if broken_links:
                return {
                    "status": "invalid",
                    "message": f"Chain integrity compromised: {len(broken_links)} broken links",
                    "verified_count": verified_count,
                    "total_count": len(entries),
                    "broken_links": broken_links
                }
            else:
                return {
                    "status": "valid",
                    "message": "Chain integrity verified",
                    "verified_count": verified_count,
                    "total_count": len(entries)
                }
                
        except Exception as e:
            logger.error(f"Error verifying chain integrity: {e}")
            return {
                "status": "error",
                "message": f"Error during verification: {str(e)}"
            }

# Global blockchain simulator instance
blockchain_simulator = BlockchainSimulator()