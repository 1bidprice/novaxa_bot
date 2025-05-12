import json
import os
from datetime import datetime

DATA_DIR = "/home/ubuntu/workspace/novaxa_bot/data"
CRM_DATA_FILE = os.path.join(DATA_DIR, "customers.json")

class CRMModule:
    def __init__(self):
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        self.customers = self._load_customers()

    def _load_customers(self):
        if not os.path.exists(CRM_DATA_FILE):
            return {}
        try:
            with open(CRM_DATA_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    def _save_customers(self):
        with open(CRM_DATA_FILE, "w") as f:
            json.dump(self.customers, f, indent=4)

    def add_customer(self, name, email, telegram_id, status, project_association=None, notes=""):
        if telegram_id in self.customers:
            return False, "Customer with this Telegram ID already exists."
        
        customer_id = f"CUST_{len(self.customers) + 1:03d}"
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        self.customers[telegram_id] = {
            "customer_id": customer_id,
            "name": name,
            "email": email,
            "telegram_id": telegram_id,
            "status": status,
            "project_association": project_association if project_association else [],
            "notes": notes,
            "created_at": timestamp,
            "updated_at": timestamp
        }
        self._save_customers()
        return True, f"Customer {name} added successfully with ID {customer_id}."

    def find_customer(self, identifier, search_by="telegram_id"):
        if search_by == "telegram_id":
            return self.customers.get(identifier)
        elif search_by == "email":
            for cust_data in self.customers.values():
                if cust_data["email"] == identifier:
                    return cust_data
        elif search_by == "name":
            results = []
            for cust_data in self.customers.values():
                if identifier.lower() in cust_data["name"].lower():
                    results.append(cust_data)
            return results if results else None
        return None

    def update_customer_status(self, telegram_id, new_status):
        if telegram_id not in self.customers:
            return False, "Customer not found."
        self.customers[telegram_id]["status"] = new_status
        self.customers[telegram_id]["updated_at"] = datetime.utcnow().isoformat() + "Z"
        self._save_customers()
        return True, f"Customer {telegram_id} status updated to {new_status}."

    def add_note_to_customer(self, telegram_id, note):
        if telegram_id not in self.customers:
            return False, "Customer not found."
        
        existing_notes = self.customers[telegram_id].get("notes", "")
        new_note_entry = f"\n[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}] {note}"
        self.customers[telegram_id]["notes"] = existing_notes + new_note_entry if existing_notes else note
        self.customers[telegram_id]["updated_at"] = datetime.utcnow().isoformat() + "Z"
        self._save_customers()
        return True, f"Note added to customer {telegram_id}."

    def get_customer_projects(self, telegram_id):
        customer = self.find_customer(telegram_id)
        if customer:
            return customer.get("project_association", [])
        return None

# Example Usage (for testing locally - will be removed or commented out later)
if __name__ == "__main__":
    crm = CRMModule()
    # Test adding a customer
    # crm.add_customer("John Doe", "john.doe@example.com", "123456789", "Lead", ["BidPrice"], "Initial contact.")
    # crm.add_customer("Jane Smith", "jane.smith@example.com", "987654321", "Active Client", ["Amesis", "Project6225"], "Long term client.")
    
    # Test finding a customer
    # print("Find by Telegram ID:", crm.find_customer("123456789"))
    # print("Find by Email:", crm.find_customer("jane.smith@example.com", search_by="email"))
    # print("Find by Name:", crm.find_customer("John", search_by="name"))

    # Test updating status
    # crm.update_customer_status("123456789", "Active Client_BidPrice")
    # print("After status update:", crm.find_customer("123456789"))

    # Test adding a note
    # crm.add_note_to_customer("987654321", "Discussed new requirements.")
    # print("After adding note:", crm.find_customer("987654321"))

    # Test getting projects
    # print("Projects for 123456789:", crm.get_customer_projects("123456789"))
    pass
