import json
import os
import re
from datetime import datetime

DATA_DIR = "/home/ubuntu/workspace/novaxa_bot/data"
TRIGGERS_FILE = os.path.join(DATA_DIR, "triggers.json")
RESPONSES_FILE = os.path.join(DATA_DIR, "responses.json")
MAPPINGS_FILE = os.path.join(DATA_DIR, "mappings.json")

class SmartReplyEngine:
    def __init__(self, crm_module=None):
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        self.triggers = self._load_data(TRIGGERS_FILE, {})
        self.responses = self._load_data(RESPONSES_FILE, {})
        self.mappings = self._load_data(MAPPINGS_FILE, [])
        self.crm_module = crm_module

    def _load_data(self, file_path, default_data):
        if not os.path.exists(file_path):
            # Create empty file if it doesn't exist
            with open(file_path, "w") as f:
                if isinstance(default_data, list):
                    json.dump([], f)
                else:
                    json.dump({}, f)
            return default_data
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return default_data

    def _save_triggers(self):
        with open(TRIGGERS_FILE, "w") as f:
            json.dump(self.triggers, f, indent=4)

    def _save_responses(self):
        with open(RESPONSES_FILE, "w") as f:
            json.dump(self.responses, f, indent=4)

    def _save_mappings(self):
        with open(MAPPINGS_FILE, "w") as f:
            json.dump(self.mappings, f, indent=4)

    # --- Trigger Management ---
    def add_trigger(self, trigger_phrase, match_type, intent=None, priority=10, is_active=True):
        trigger_id = f"TRG_{len(self.triggers) + 1:03d}"
        timestamp = datetime.utcnow().isoformat() + "Z"
        self.triggers[trigger_id] = {
            "trigger_id": trigger_id,
            "trigger_phrase": trigger_phrase,
            "match_type": match_type,  # "exact", "contains", "regex"
            "intent": intent,
            "is_active": is_active,
            "priority": priority,
            "created_at": timestamp,
            "updated_at": timestamp
        }
        self._save_triggers()
        return True, f"Trigger {trigger_id} added successfully."

    # --- Response Management ---
    def add_response(self, response_text, response_type="text", attachments=None, follow_up_action_id=None, is_active=True):
        response_id = f"RES_{len(self.responses) + 1:03d}"
        timestamp = datetime.utcnow().isoformat() + "Z"
        self.responses[response_id] = {
            "response_id": response_id,
            "response_text": response_text,
            "response_type": response_type, # "text", "markdown", "image_url", "document_url"
            "attachments": attachments if attachments else [],
            "follow_up_action_id": follow_up_action_id,
            "is_active": is_active,
            "created_at": timestamp,
            "updated_at": timestamp
        }
        self._save_responses()
        return True, f"Response {response_id} added successfully."

    # --- Mapping Management ---
    def add_mapping(self, trigger_id, response_id, conditions=None, order_in_sequence=1, is_active=True):
        if trigger_id not in self.triggers:
            return False, f"Trigger ID {trigger_id} not found."
        if response_id not in self.responses:
            return False, f"Response ID {response_id} not found."
        
        mapping_id = f"MAP_{len(self.mappings) + 1:03d}"
        timestamp = datetime.utcnow().isoformat() + "Z"
        new_mapping = {
            "mapping_id": mapping_id,
            "trigger_id": trigger_id,
            "response_id": response_id,
            "conditions": conditions if conditions else {},
            "order_in_sequence": order_in_sequence,
            "is_active": is_active,
            "created_at": timestamp,
            "updated_at": timestamp
        }
        self.mappings.append(new_mapping)
        self._save_mappings()
        return True, f"Mapping {mapping_id} added successfully."

    def _preprocess_message(self, message_text):
        return message_text.lower().strip()

    def _format_response(self, response_text, crm_data=None, matched_groups=None):
        # Basic placeholder replacement
        if crm_data:
            for key, value in crm_data.items():
                response_text = response_text.replace(f"{{crm_{key}}}", str(value))
        if matched_groups:
            for i, group in enumerate(matched_groups):
                response_text = response_text.replace(f"{{regex_group_{i+1}}}", str(group))
        # Add more complex placeholder logic as needed (e.g. {pricelist_url})
        # For now, this is a simple implementation.
        return response_text

    def process_message(self, message_text, user_telegram_id=None, crm_data=None):
        processed_text = self._preprocess_message(message_text)
        matched_trigger = None
        regex_groups = None

        # Sort triggers by priority (lower number means higher priority)
        sorted_triggers = sorted(self.triggers.values(), key=lambda t: t.get("priority", 10))

        for trigger in sorted_triggers:
            if not trigger.get("is_active", False):
                continue

            trigger_phrase = trigger.get("trigger_phrase", "").lower()
            match_type = trigger.get("match_type", "exact")

            if match_type == "exact" and processed_text == trigger_phrase:
                matched_trigger = trigger
                break
            elif match_type == "contains" and trigger_phrase in processed_text:
                matched_trigger = trigger
                break
            elif match_type == "regex":
                try:
                    match = re.search(trigger_phrase, processed_text, re.IGNORECASE)
                    if match:
                        matched_trigger = trigger
                        regex_groups = match.groups()
                        break
                except re.error:
                    # Invalid regex, skip this trigger or log an error
                    print(f"Warning: Invalid regex for trigger {trigger.get('trigger_id')}: {trigger_phrase}")
                    continue
        
        if not matched_trigger:
            return None # Or a default response object

        # Find mappings for the matched trigger
        applicable_mappings = []
        for mapping in self.mappings:
            if mapping.get("trigger_id") == matched_trigger.get("trigger_id") and mapping.get("is_active", False):
                # TODO: Implement condition evaluation (e.g., CRM based)
                # For now, all active mappings for the trigger are considered applicable
                applicable_mappings.append(mapping)
        
        if not applicable_mappings:
            return None

        # Sort by order_in_sequence if multiple responses are planned (not fully implemented here)
        # For now, take the first applicable mapping
        selected_mapping = sorted(applicable_mappings, key=lambda m: m.get("order_in_sequence", 1))[0]
        response_id = selected_mapping.get("response_id")
        
        if response_id and response_id in self.responses:
            response_template = self.responses[response_id]
            if response_template.get("is_active", False):
                # Get CRM data if not already provided and crm_module exists
                current_crm_data = crm_data
                if not current_crm_data and self.crm_module and user_telegram_id:
                    current_crm_data = self.crm_module.find_customer(str(user_telegram_id))
                
                formatted_text = self._format_response(
                    response_template.get("response_text", ""), 
                    crm_data=current_crm_data, 
                    matched_groups=regex_groups
                )
                return {
                    "text": formatted_text,
                    "response_type": response_template.get("response_type", "text"),
                    "attachments": response_template.get("attachments", [])
                }
        return None

# Example Usage (for testing locally)
if __name__ == "__main__":
    # Dummy CRM for testing
    class DummyCRM:
        def find_customer(self, telegram_id):
            if telegram_id == "123":
                return {"name": "Test User", "status": "VIP"}
            return None

    sre = SmartReplyEngine(crm_module=DummyCRM())

    # Ensure data files are empty or contain valid JSON for a clean test
    for f_path in [TRIGGERS_FILE, RESPONSES_FILE, MAPPINGS_FILE]:
        if os.path.exists(f_path):
            os.remove(f_path)
    sre = SmartReplyEngine(crm_module=DummyCRM()) # Re-initialize to create files

    # Add some triggers
    sre.add_trigger("hello", "exact", "greeting")
    sre.add_trigger("τιμή", "contains", "pricing_query", priority=5)
    sre.add_trigger(r"how much is (.+)", "regex", "pricing_query_specific")
    sre.add_trigger("my name is", "contains", "name_mention")

    # Add some responses
    sre.add_response("Hello there {crm_name}! How can I help you today?", "text") # RES_001
    sre.add_response("For pricing information, please visit {pricelist_url} or tell me what product you are interested in.", "markdown") # RES_002
    sre.add_response("The price for {regex_group_1} is $X.XX. More details at {pricelist_url}", "markdown") # RES_003
    sre.add_response("Nice to meet you, {crm_name}! Your status is {crm_status}.", "text") # RES_004

    # Add some mappings
    sre.add_mapping("TRG_001", "RES_001") # hello -> Hello there {crm_name}!
    sre.add_mapping("TRG_002", "RES_002") # τιμή -> For pricing information...
    sre.add_mapping("TRG_003", "RES_003") # how much is (.+) -> The price for {regex_group_1}...
    sre.add_mapping("TRG_004", "RES_004") # my name is -> Nice to meet you, {crm_name}!

    print("--- Test 1: Hello (User 123) ---")
    result1 = sre.process_message("hello", user_telegram_id="123")
    print(result1)

    print("\n--- Test 2: Τιμή ---")
    result2 = sre.process_message("ποια είναι η τιμή για το προϊόν Χ;")
    print(result2)

    print("\n--- Test 3: Regex ---")
    result3 = sre.process_message("how much is the new widget")
    print(result3)

    print("\n--- Test 4: No Match ---")
    result4 = sre.process_message("this should not match anything")
    print(result4)

    print("\n--- Test 5: CRM Context (User 123) ---")
    result5 = sre.process_message("my name is mentioned", user_telegram_id="123") # TRG_004 mapped to RES_004
    print(result5)

    print("\n--- Test 6: CRM Context (User 456 - unknown) ---")
    result6 = sre.process_message("my name is mentioned", user_telegram_id="456")
    print(result6)

    print(f"\nTriggers: {sre.triggers}")
    print(f"Responses: {sre.responses}")
    print(f"Mappings: {sre.mappings}")

