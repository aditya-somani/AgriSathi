import sqlite3
import logging
import os
from datetime import datetime
from typing import Optional, List, Dict

logger = logging.getLogger("agrisathi.db")

class FarmerDB:
    """
    The 'Memory Bank' of AgriSathi.
    Handles persistent storage of farmer profiles and conversation history.
    """
    
    def __init__(self, db_path: str = "data/agrisathi.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Initializes the database schema"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Table 1: Farmer Profiles
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS farmers (
                    phone TEXT PRIMARY KEY,
                    name TEXT,
                    place TEXT,
                    state TEXT,
                    crops TEXT,
                    preferred_language TEXT DEFAULT 'hindi',
                    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table 2: Conversations
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone TEXT,
                    summary TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (phone) REFERENCES farmers (phone)
                )
            ''')
            
            # Migrations are handled by schema above for new setups
            conn.commit()
            logger.info("Database initialized successfully")

    def get_farmer(self, phone: str) -> Optional[Dict]:
        """Fetches a farmer's profile and their last 5 conversation summaries"""
        with self._get_connection() as conn:
            # Normally, SQLite returns data as lists (like [name, village, ...]). By setting this, we get data as dictionaries (like {name: "Ramesh", village: ...}).
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM farmers WHERE phone = ?", (phone,))
            farmer = cursor.fetchone()
            
            if not farmer:
                return None
            
            cursor.execute('''
                SELECT summary FROM conversations 
                WHERE phone = ? 
                ORDER BY timestamp DESC LIMIT 5
            ''', (phone,))
            summaries = [row['summary'] for row in cursor.fetchall()]
            
            return {
                "name": farmer['name'],
                "place": farmer['place'],
                "state": farmer['state'],
                "crops": farmer['crops'],
                "preferred_language": farmer['preferred_language'] or 'hindi',
                "history": summaries
            }

    def register_farmer(self, phone: str, name: str, place: str, state: str, crops: str, language: str = "hindi"):
        """Creates or updates a farmer's profile"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO farmers (phone, name, place, state, crops, preferred_language)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (phone, name, place, state, crops, language))
            conn.commit()
            logger.info(f"Farmer {name} ({phone}) registered/updated in {place}, {state}")

    def update_language(self, phone: str, language: str):
        """Updates ONLY the preferred language - can be called mid-conversation"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE farmers SET preferred_language = ? WHERE phone = ?
            ''', (language, phone))
            conn.commit()
            logger.info(f"Language updated to {language} for {phone}")

    def update_farmer_details(self, phone: str, name: str = None, place: str = None, state: str = None, crops: str = None):
        """Updates specific fields of a farmer's profile"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Dynamic query building
            updates = []
            params = []
            
            if name:
                updates.append("name = ?")
                params.append(name)
            if place:
                updates.append("place = ?")
                params.append(place)
            if state:
                updates.append("state = ?")
                params.append(state)
            if crops:
                updates.append("crops = ?")
                params.append(crops)
                
            if not updates:
                return # Nothing to update
                
            params.append(phone)
            query = f"UPDATE farmers SET {', '.join(updates)} WHERE phone = ?"
            
            cursor.execute(query, tuple(params))
            conn.commit()
            logger.info(f"Updated profile for {phone}: {updates}")

    def add_summary(self, phone: str, summary: str):
        """
        Records a new conversation summary.
        Enforces a limit of 5 conversations per farmer - oldest gets deleted.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 1. Insert the new summary first
            cursor.execute('''
                INSERT INTO conversations (phone, summary)
                VALUES (?, ?)
            ''', (phone, summary))
            
            # 2. Enforce the 5-conversation limit by deleting oldest entries
            # We keep only the 5 most recent by timestamp
            cursor.execute('''
                DELETE FROM conversations 
                WHERE phone = ? AND id NOT IN (
                    SELECT id FROM conversations 
                    WHERE phone = ? 
                    ORDER BY timestamp DESC 
                    LIMIT 5
                )
            ''', (phone, phone))
            
            conn.commit()
            logger.info(f"Summary added for {phone} (5-message limit enforced)")



# Singleton instance
db = FarmerDB()
