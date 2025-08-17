"""
Database configuration and connection management.
Currently using in-memory storage, but can be extended to use a real database.
"""

from typing import Dict, Any
import json
import os
from pathlib import Path

# In-memory storage (replace with database in production)
venues_db: Dict[str, Any] = {}

def save_data_to_file():
    """Save in-memory data to JSON files (for persistence)"""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    with open(data_dir / "venues.json", "w") as f:
        json.dump(venues_db, f, default=str, indent=2)

def load_data_from_file():
    """Load data from JSON files into memory"""
    data_dir = Path("data")
    
    try:
        if (data_dir / "venues.json").exists():
            with open(data_dir / "venues.json", "r") as f:
                venues_db.update(json.load(f))
    except Exception as e:
        print(f"Error loading venues: {e}")

# Load data on module import
load_data_from_file()
