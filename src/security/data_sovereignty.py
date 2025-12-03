import logging
import json
import time
import hashlib
from enum import Enum
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataClassification(Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    TOP_SECRET = "top_secret"

class DataSovereignty:
    """
    Implements Automotive Data Sovereignty controls including classification,
    exfiltration prevention, blockchain audit logging, and geo-fencing.
    """

    def __init__(self):
        self.blockchain_ledger = []
        self.geo_policies = {
            "US": [DataClassification.TOP_SECRET, DataClassification.SECRET],
            "EU": [DataClassification.CONFIDENTIAL],
            "GLOBAL": [DataClassification.PUBLIC]
        }
        logger.info("DataSovereignty module initialized.")

    def classify_data(self, data: Any, source: str) -> DataClassification:
        """
        Classifies data based on source and content.
        
        Args:
            data: The data object or content.
            source: The origin of the data (e.g., 'engine_ecu', 'infotainment').
            
        Returns:
            DataClassification tag.
        """
        # Rule-based classification engine
        if source == "engine_ecu":
            return DataClassification.CONFIDENTIAL
        elif source == "navigation_history":
            return DataClassification.SECRET
        elif source == "military_comms":
            return DataClassification.TOP_SECRET
        elif source == "infotainment":
            return DataClassification.PUBLIC
        
        return DataClassification.INTERNAL

    def check_exfiltration_policy(self, data_tag: DataClassification, destination: str) -> bool:
        """
        Enforces policy preventing unauthorized exfiltration.
        
        Args:
            data_tag: The classification of the data.
            destination: The target destination (e.g., 'cloud_storage', 'external_drive').
            
        Returns:
            bool: True if transfer is allowed, False otherwise.
        """
        logger.info(f"Checking exfiltration policy for {data_tag.value} to {destination}")
        
        # Strict policy: Top Secret and Secret cannot leave the vehicle/secure edge
        if data_tag in [DataClassification.TOP_SECRET, DataClassification.SECRET]:
            if destination in ["cloud_storage", "public_internet", "external_drive"]:
                logger.critical(f"BLOCKED exfiltration of {data_tag.value} data to {destination}")
                self.log_audit_event("EXFILTRATION_ATTEMPT", f"Blocked {data_tag.value} to {destination}")
                return False
        
        return True

    def log_audit_event(self, event_type: str, details: str):
        """
        Logs an event to an immutable blockchain ledger (Simulated).
        """
        timestamp = time.time()
        # Create a hash chain to simulate blockchain immutability
        previous_hash = self.blockchain_ledger[-1]['hash'] if self.blockchain_ledger else "0" * 64
        
        entry = {
            "timestamp": timestamp,
            "event_type": event_type,
            "details": details,
            "previous_hash": previous_hash
        }
        
        # Calculate hash of this entry
        entry_str = json.dumps(entry, sort_keys=True)
        entry_hash = hashlib.sha256(entry_str.encode()).hexdigest()
        entry['hash'] = entry_hash
        
        self.blockchain_ledger.append(entry)
        logger.info(f"Audit Logged: {event_type} - {details} (Hash: {entry_hash[:8]}...)")

    def enforce_geo_fencing(self, current_location_country: str, data_tag: DataClassification) -> bool:
        """
        Restricts data access based on geographic location (Cross-border restrictions).
        
        Args:
            current_location_country: ISO country code (e.g., 'US', 'CN', 'DE').
            data_tag: The classification of the data being accessed.
            
        Returns:
            bool: True if access is allowed in this location.
        """
        # If data is Top Secret, it might only be accessible in US
        if data_tag == DataClassification.TOP_SECRET and current_location_country != "US":
             logger.warning(f"Geo-fencing: Access to TOP_SECRET denied in {current_location_country}")
             return False
             
        # Example: GDPR restrictions might apply, handled here
        
        logger.info(f"Geo-fencing: Access to {data_tag.value} allowed in {current_location_country}")
        return True

# Example Usage
if __name__ == "__main__":
    ds = DataSovereignty()
    tag = ds.classify_data({}, "military_comms")
    ds.check_exfiltration_policy(tag, "cloud_storage")
    ds.log_audit_event("ACCESS_GRANT", "User accessed engine logs")
    ds.enforce_geo_fencing("DE", DataClassification.TOP_SECRET)
