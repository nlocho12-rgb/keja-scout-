import os
import json

class LocalStorageEngine:
    def __init__(self, directory_path: str):
        self.directory = directory_path
        self.file_path = os.path.join(self.directory, "properties.json")
        self._ensure_storage_exists()

    def _ensure_storage_exists(self):
        os.makedirs(self.directory, exist_ok=True)
        if not os.path.exists(self.file_path):
            mock_data = {
                "prop_001": {
                    "property_id": "prop_001",
                    "type": "Bedsitter",
                    "nearest_university": "JKUAT",
                    "nearest_landmark": "Gate C",
                    "price": 9500,
                    "deposit": 9500,
                    "gender_policy": "Mixed",
                    "utilities": {"water": "Borehole (Constant)", "electricity": "Tokens", "wifi": True},
                    "is_verified": True,
                    "is_available": True,
                    "booking_status": "Available",
                    "scam_flags": 0
                },
                "prop_002": {
                    "property_id": "prop_002",
                    "type": "Single Room",
                    "nearest_university": "Kenyatta University",
                    "nearest_landmark": "KM Stage",
                    "price": 6000,
                    "deposit": 3000,
                    "gender_policy": "Mixed",
                    "utilities": {"water": "Council (Tue/Fr)", "electricity": "Tokens", "wifi": False},
                    "is_verified": False,
                    "is_available": True,
                    "booking_status": "Available",
                    "scam_flags": 1
                },
                "prop_003": {
                    "property_id": "prop_003",
                    "type": "One Bedroom",
                    "nearest_university": "JKUAT",
                    "nearest_landmark": "Gachororo",
                    "price": 14000,
                    "deposit": 14000,
                    "gender_policy": "Mixed",
                    "utilities": {"water": "Borehole (Constant)", "electricity": "Metered", "wifi": True},
                    "is_verified": True,
                    "is_available": True,
                    "booking_status": "Available",
                    "scam_flags": 0
                }
            }
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(mock_data, f, indent=4)

    def load_all_properties(self) -> dict:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def save_changes(self, data: dict):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
