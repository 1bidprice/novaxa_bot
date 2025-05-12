import os
import sys

# Ensure the main project directory is in the Python path
# This assumes test_modules.py is in /home/ubuntu/ and novaxa_bot_phase2 is a subdirectory
# or that novaxa_bot_phase2 is directly in the Python path.
module_base_path = "/home/ubuntu/novaxa_bot_phase2"
if module_base_path not in sys.path:
    sys.path.insert(0, module_base_path)

from crm.crm_module import CRMModule
from smart_reply.smart_reply_engine import SmartReplyEngine

def test_crm_module(crm):
    print("--- Testing CRM Module ---")
    # Clean up old data for consistent testing if file exists
    if os.path.exists(crm.CRM_DATA_FILE):
        os.remove(crm.CRM_DATA_FILE)
        crm.customers = crm._load_customers() # Reload empty

    print("Adding customer John Doe...")
    success, msg = crm.add_customer("John Doe", "john.doe@example.com", "user123", "Lead", ["BidPrice"], "Initial contact.")
    print(f"Result: {success}, {msg}")

    print("Adding customer Jane Smith...")
    success, msg = crm.add_customer("Jane Smith", "jane.smith@example.com", "user456", "Active Client", ["Amesis"], "Important client.")
    print(f"Result: {success}, {msg}")

    print("\nFinding customer John (by name)...")
    john = crm.find_customer("John", search_by="name")
    print(f"Found: {john}")

    print("\nFinding customer user456 (by Telegram ID)...")
    jane = crm.find_customer("user456")
    print(f"Found: {jane}")

    if jane:
        print("\nUpdating Jane Smith's status to 'On Hold'...")
        success, msg = crm.update_customer_status("user456", "On Hold")
        print(f"Result: {success}, {msg}")
        print(f"Jane after update: {crm.find_customer('user456')}")

        print("\nAdding note to Jane Smith...")
        success, msg = crm.add_note_to_customer("user456", "Follow up next week.")
        print(f"Result: {success}, {msg}")
        print(f"Jane after note: {crm.find_customer('user456')}") # Corrected line
    print("--- CRM Module Test Complete ---\n")

def test_sre_module(sre, crm_module_instance):
    print("--- Testing Smart Reply Engine ---")
    # Clean up old data for consistent testing
    if os.path.exists(sre.TRIGGERS_FILE): os.remove(sre.TRIGGERS_FILE)
    if os.path.exists(sre.RESPONSES_FILE): os.remove(sre.RESPONSES_FILE)
    if os.path.exists(sre.MAPPINGS_FILE): os.remove(sre.MAPPINGS_FILE)
    sre.triggers = sre._load_data(sre.TRIGGERS_FILE, {})
    sre.responses = sre._load_data(sre.RESPONSES_FILE, {})
    sre.mappings = sre._load_data(sre.MAPPINGS_FILE, [])

    print("Adding trigger 'hello'...")
    sre.add_trigger("hello", "exact", "greeting")
    trg_hello_id = list(sre.triggers.keys())[0] # Assuming it's the first one

    print("Adding trigger 'τιμή'...")
    sre.add_trigger("τιμή", "contains", "pricing_query")
    trg_price_id = list(sre.triggers.keys())[1]

    print("\nAdding response for greeting...")
    sre.add_response("Hello {user_name}! How can I help?", "text")
    res_greeting_id = list(sre.responses.keys())[0]

    print("Adding response for pricing...")
    sre.add_response("For prices, please check {pricelist_url}", "markdown")
    res_pricing_id = list(sre.responses.keys())[1]

    print("\nMapping 'hello' trigger to greeting response...")
    sre.add_mapping(trg_hello_id, res_greeting_id)
    print("Mapping 'τιμή' trigger to pricing response...")
    sre.add_mapping(trg_price_id, res_pricing_id)

    print("\nProcessing message 'hello' for user123 (John Doe)...")
    john_crm_data = crm_module_instance.find_customer("user123")
    response1 = sre.process_message("hello", user_telegram_id="user123", crm_data=john_crm_data)
    print(f"Response: {response1}")

    print("\nProcessing message 'ποια είναι η τιμή;' for user456 (Jane Smith)...")
    jane_crm_data = crm_module_instance.find_customer("user456")
    response2 = sre.process_message("ποια είναι η τιμή;", user_telegram_id="user456", crm_data=jane_crm_data)
    print(f"Response: {response2}")

    print("\nProcessing message 'unknown query'...")
    response3 = sre.process_message("this is an unknown query")
    print(f"Response: {response3}") 
    # Expecting None or a default fallback if implemented in SRE, currently SRE returns None if no match

    print("--- Smart Reply Engine Test Complete ---")

if __name__ == "__main__":
    # Initialize CRM module first as SRE might depend on it
    crm_instance = CRMModule()
    test_crm_module(crm_instance)

    # Initialize SRE with the CRM instance
    sre_instance = SmartReplyEngine(crm_module=crm_instance)
    test_sre_module(sre_instance, crm_instance)

    print("\nAll module tests concluded.")
    print(f"CRM data is in: {crm_instance.CRM_DATA_FILE}")
    print(f"SRE trigger data is in: {sre_instance.TRIGGERS_FILE}")
    print(f"SRE response data is in: {sre_instance.RESPONSES_FILE}")
    print(f"SRE mapping data is in: {sre_instance.MAPPINGS_FILE}")

