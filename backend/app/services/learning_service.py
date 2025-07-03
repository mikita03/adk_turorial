import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import os

class LearningService:
    def __init__(self):
        vector_db_path = os.getenv("VECTOR_DB_PATH", "./vector_db")
        os.makedirs(vector_db_path, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=vector_db_path)
        
        self.corrections_collection = self.client.get_or_create_collection(
            name="email_corrections",
            metadata={"description": "User corrections for learning"}
        )
        
        self.profiles_collection = self.client.get_or_create_collection(
            name="recipient_profiles",
            metadata={"description": "Recipient preferences and profiles"}
        )
    
    async def save_correction(self, original: str, corrected: str, context: Dict[str, Any]):
        """Save user correction for learning"""
        try:
            correction_id = f"correction_{datetime.now().timestamp()}"
            
            self.corrections_collection.add(
                documents=[corrected],
                metadatas=[{
                    "original": original,
                    "recipient": context.get("recipient", ""),
                    "timestamp": context.get("timestamp", datetime.now().isoformat()),
                    "correction_type": context.get("correction_type", "general"),
                    "context": json.dumps(context)
                }],
                ids=[correction_id]
            )
            
            await self._update_recipient_profile(context.get("recipient", ""), original, corrected, context)
            
            return True
        except Exception as e:
            print(f"Error saving correction: {e}")
            return False
    
    async def get_similar_corrections(self, draft: str, recipient: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get similar corrections for the recipient"""
        try:
            results = self.corrections_collection.query(
                query_texts=[draft],
                n_results=limit,
                where={"recipient": recipient} if recipient else None
            )
            
            similar_corrections = []
            if results["documents"]:
                for i, doc in enumerate(results["documents"][0]):
                    metadata = results["metadatas"][0][i]
                    similar_corrections.append({
                        "corrected": doc,
                        "original": metadata.get("original", ""),
                        "timestamp": metadata.get("timestamp", ""),
                        "correction_type": metadata.get("correction_type", ""),
                        "distance": results["distances"][0][i] if results["distances"] else 0.0
                    })
            
            return similar_corrections
        except Exception as e:
            print(f"Error getting similar corrections: {e}")
            return []
    
    async def get_recipient_profile(self, recipient: str) -> Optional[Dict[str, Any]]:
        """Get recipient profile and preferences"""
        try:
            results = self.profiles_collection.query(
                query_texts=[recipient],
                n_results=1,
                where={"recipient": recipient}
            )
            
            if results["documents"] and results["documents"][0]:
                metadata = results["metadatas"][0][0]
                return {
                    "recipient": recipient,
                    "preferences": json.loads(metadata.get("preferences", "{}")),
                    "summary": json.loads(metadata.get("summary", "{}")),
                    "importance": metadata.get("importance", 0.5),
                    "last_updated": metadata.get("last_updated", "")
                }
            
            return None
        except Exception as e:
            print(f"Error getting recipient profile: {e}")
            return None
    
    async def _update_recipient_profile(self, recipient: str, original: str, corrected: str, context: Dict[str, Any]):
        """Update recipient profile based on correction"""
        try:
            existing_profile = await self.get_recipient_profile(recipient)
            
            if existing_profile:
                preferences = existing_profile.get("preferences", {})
            else:
                preferences = {}
            
            correction_analysis = await self._analyze_correction(original, corrected, context)
            
            for key, value in correction_analysis.items():
                if key in preferences:
                    if isinstance(preferences[key], list):
                        if value not in preferences[key]:
                            preferences[key].append(value)
                    else:
                        preferences[key] = value
                else:
                    preferences[key] = value
            
            profile_id = f"profile_{recipient}_{datetime.now().timestamp()}"
            
            self.profiles_collection.upsert(
                documents=[recipient],
                metadatas=[{
                    "recipient": recipient,
                    "preferences": json.dumps(preferences),
                    "summary": json.dumps({"last_correction": datetime.now().isoformat()}),
                    "importance": 0.8,  # Default importance
                    "last_updated": datetime.now().isoformat()
                }],
                ids=[profile_id]
            )
            
        except Exception as e:
            print(f"Error updating recipient profile: {e}")
    
    async def _analyze_correction(self, original: str, corrected: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze correction to extract preferences"""
        preferences = {}
        
        
        if "です・ます" in corrected and "である" in original:
            preferences["formality_level"] = "high"
        elif "である" in corrected and "です・ます" in original:
            preferences["formality_level"] = "low"
        
        if "恐れ入りますが" in corrected:
            preferences.setdefault("preferred_expressions", []).append("恐れ入りますが")
        
        if "よろしくお願いします" not in corrected and "よろしくお願いします" in original:
            preferences.setdefault("avoid_expressions", []).append("よろしくお願いします")
        
        if "(" in corrected and "曜日" in corrected:
            preferences["date_format"] = "include_day_of_week"
        
        return preferences
    
    async def get_learning_stats(self) -> Dict[str, Any]:
        """Get learning system statistics"""
        try:
            corrections_count = self.corrections_collection.count()
            profiles_count = self.profiles_collection.count()
            
            return {
                "total_corrections": corrections_count,
                "total_profiles": profiles_count,
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error getting learning stats: {e}")
            return {
                "total_corrections": 0,
                "total_profiles": 0,
                "last_updated": datetime.now().isoformat()
            }
