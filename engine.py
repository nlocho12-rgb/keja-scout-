import time

class HousingEngine:
    def __init__(self, storage_engine):
        self.storage = storage_engine
        self.memory_db = self.storage.load_all_properties()
        self.user_registry = {
            "demo_student": {"role": "student", "has_uploaded_id": True, "is_verified": True},
            "demo_landlord": {"role": "landlord", "has_uploaded_id": True, "is_verified": False}
        }

    def get_all_properties(self) -> list:
        self.memory_db = self.storage.load_all_properties()
        return [item for item in self.memory_db.values() if item.get("is_available", True)]

    def register_user(self, user_id: str, role: str):
        self.user_registry[user_id] = {
            "role": role,
            "has_uploaded_id": False,
            "is_verified": False
        }
        return self.user_registry[user_id]

    def submit_verification_id(self, user_id: str, document_name: str):
        if user_id in self.user_registry:
            self.user_registry[user_id]["has_uploaded_id"] = True
            if self.user_registry[user_id]["role"] == "student":
                self.user_registry[user_id]["is_verified"] = True
            return True, "Verification file successfully processed."
        return False, "User account profile not found."

    def search_and_filter(self, university: str, max_budget: int = None, property_type: str = None):
        self.memory_db = self.storage.load_all_properties()
        filtered = []
        for item in self.memory_db.values():
            if not item.get("is_available", True) or item.get("booking_status") == "Pending":
                continue
            if item.get("scam_flags", 0) >= 3:
                continue
            if item["nearest_university"].lower() != university.lower():
                continue
            if max_budget and item["price"] > max_budget:
                continue
            if property_type and item["type"].lower() != property_type.lower():
                continue
            filtered.append(item)
        return filtered

    def process_safelock_trigger(self, property_id: str, user_id: str):
        user = self.user_registry.get(user_id, {"is_verified": False})
        if not user["is_verified"]:
            return False, "Verification Denied: Student School ID must be uploaded before Escrow Booking."

        self.memory_db = self.storage.load_all_properties()
        if property_id in self.memory_db:
            item = self.memory_db[property_id]
            item["booking_status"] = "Pending"
            item["safelock_deadline"] = time.time() + 7200  
            item["locked_by_user"] = user_id
            self.storage.save_changes(self.memory_db)
            return True, "SafeLock Activated! 10% Escrow safe. Landlord 2-Hour confirmation window open."
        return False, "Target room listing could not be referenced."

    def resolve_safelock(self, property_id: str, landlord_confirmed: bool):
        self.memory_db = self.storage.load_all_properties()
        if property_id in self.memory_db:
            item = self.memory_db[property_id]
            if landlord_confirmed:
                item["booking_status"] = "Taken"
                item["is_available"] = False
                msg = "Booking verified! 10% committed. Unlocking caretaker contact channels."
            else:
                item["booking_status"] = "Available"
                item["locked_by_user"] = None
                msg = "Reservation cancelled. 10% Escrow deposit reversed to student M-Pesa ledger."
            self.storage.save_changes(self.memory_db)
            return True, msg
        return False, "Target room listing could not be referenced."

    def report_listing(self, property_id: str):
        self.memory_db = self.storage.load_all_properties()
        if property_id in self.memory_db:
            self.memory_db[property_id]["scam_flags"] += 1
            if self.memory_db[property_id]["scam_flags"] >= 3:
                self.memory_db[property_id]["is_available"] = False
                self.storage.save_changes(self.memory_db)
                return True, "Listing automatically suspended. Dropped to Admin Queue for National ID audit."
            self.storage.save_changes(self.memory_db)
            return True, f"Scam report filed. Active flags: {self.memory_db[property_id]['scam_flags']}/3"
        return False, "Error processing report."
