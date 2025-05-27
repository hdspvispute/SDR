import re

def extract_lead_details(message: str) -> dict:
    details = {
        "name": None,
        "email": None,
        "company": None
    }

    # Basic email extraction
    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', message)
    if email_match:
        details["email"] = email_match.group(0)

    # Basic company extraction (very naive)
    # Looks for common suffixes or words following "company is" or "company:"
    company_match = re.search(r"(?i)(?:company is|company:|works at|working at|from)\s*([A-Za-z0-9\s,&.'-]+(?:Corp\.|Inc\.|Ltd\.|LLC)?)", message)
    if company_match and company_match.group(1):
        company_name = company_match.group(1).strip()
        # Remove any leading/trailing commas or periods that might be part of the regex capture but not the name
        company_name = company_name.strip(' .,')
        details["company"] = company_name.replace("Corp.", "Corp").replace("Inc.", "Inc").replace("Ltd.", "Ltd").replace("LLC", "LLC")
    else:
        # Fallback: Look for capitalized words that might be a company, avoiding email domain
        # Adjusted regex to better capture multi-word company names and common patterns
        potential_companies = re.findall(r"\b[A-Z][A-Za-z0-9'&.-]*(?:\s+[A-Z][A-Za-z0-9'&.-]+)*\b(?:\s*(?:Corp|Inc|Ltd|LLC))?", message)
        if details["email"]:
            domain = details["email"].split('@')[1].lower()
            # Filter out parts of the email domain and common short words
            potential_companies = [
                pc.strip() for pc in potential_companies if pc.lower() not in ["hello", "hi", "lead", "contact", "name", "email", "company"] and not domain.startswith(pc.lower().split('.')[0].split(' ')[0])
            ]
        
        if potential_companies:
            # Prefer longer names or names with company suffixes if primary regex failed
            # This is still heuristic.
            sorted_companies = sorted(potential_companies, key=lambda x: (any(s in x for s in ["Corp", "Inc", "Ltd", "LLC"]), len(x)), reverse=True)
            if sorted_companies:
                details["company"] = sorted_companies[0]


    # Basic name extraction (very naive)
    name_match = re.search(r"(?i)(?:name is|contact is|I am|lead is)\s*([A-Z][a-z]+(?:\s+[A-Z][a-z'-]+){0,2})", message)
    if name_match and name_match.group(1):
        potential_name = name_match.group(1).strip()
        if not details["company"] or potential_name.lower() not in details["company"].lower():
             details["name"] = potential_name
    else:
        # Fallback: Look for sequences of capitalized words not already part of the company
        potential_names = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z'-]+){0,2}\b", message)
        if potential_names:
            for pn in potential_names:
                is_part_of_company = details["company"] and pn.lower() in details["company"].lower().split(' ')[0].lower() # check against first word of company
                is_intro_word = pn.lower() in ["hello", "hi", "lead", "contact", "email", "company", "corp", "inc", "ltd", "llc"] 
                # Check if it's part of the email address (local part)
                is_part_of_email = details["email"] and pn.lower() in details["email"].split('@')[0].lower()

                if not is_part_of_company and not is_intro_word and not is_part_of_email:
                    details["name"] = pn
                    break 
    
    # If name is still None, and we have an email, try to infer from email (e.g., john.doe@...)
    if not details["name"] and details["email"]:
        local_part = details["email"].split('@')[0]
        # Replace common separators with space and capitalize
        potential_name_from_email = ' '.join([name_part.capitalize() for name_part in re.split(r'[\._-]', local_part) if name_part.isalpha() and len(name_part)>1])
        if potential_name_from_email:
            # Avoid setting name if it's too similar to the company name (e.g. "Sales" from sales@company.com)
            if not details["company"] or potential_name_from_email.lower() not in details["company"].lower():
                details["name"] = potential_name_from_email
    
    # Final check: if company name is part of the extracted name, remove it.
    if details["name"] and details["company"] and details["name"].endswith(details["company"]):
        details["name"] = details["name"][:-len(details["company"])].strip()

    # Ensure no field is just a common keyword if other details are present
    common_keywords = ["lead", "contact", "email", "company", "name"]
    for key in ["name", "company"]:
        if details[key] and details[key].lower() in common_keywords and any(details[other_key] for other_key in details if other_key != key):
            details[key] = None # Reset if it's a keyword and other data exists

    return details

if __name__ == '__main__':
    test_messages = [
        "The lead is Jane Doe, her email is jane.doe@example.com and she works at Example Corp.",
        "My contact is John Smith from Innovations Inc. you can reach him at john.smith@innovations.com.",
        "I want to add a new lead: Michael Brown, michael.brown@another-example.net, from Brown & Co LLC.",
        "Yes, please. Peter Jones at pjones@test.co.uk for Test Ltd",
        "The company is Super Solutions Inc. and the contact is Super Man, superman@supersolutions.com",
        "Contact Alice Wonderland, alice@wonder.land, Wonderland Adventures", # Slightly different phrasing
        "Bob The Builder bob.builder@construction.co an employee of Construction Experts Ltd.", # Name first
        "Email me at charlie.chaplin@movies.com, from Chaplin Studios.", # Email first, then company
        "David Copperfield, magic@illusions.org, Illusions LLC is the lead.", # Name, email, company together
        "This is Eve, her email is eve@garden.com and she is with Eden Corp.", # "with" for company
        "Frank N. Stein from Monster Labs Inc, frank@monsterlabs.com.", # Middle initial, company with Inc.
        "Grace Hopper, grace@navy.mil, US Navy.", # Real-world like example
        "My name is Info Desk from The Information Company. Email is info@theinformation.co." # Name could be tricky
    ]

    for i, message in enumerate(test_messages):
        print(f"Test {i+1}: '{message}' -> {extract_lead_details(message)}")

    # Test specific case from prompt example
    test_message_official_1 = "The lead is Jane Doe, her email is jane.doe@example.com and she works at Example Corp."
    print(f"Official Test 1: '{test_message_official_1}' -> {extract_lead_details(test_message_official_1)}")
    # Expected: {'name': 'Jane Doe', 'email': 'jane.doe@example.com', 'company': 'Example Corp'}

    test_message_official_2 = "My contact is John Smith from Innovations Inc. you can reach him at john.smith@innovations.com."
    print(f"Official Test 2: '{test_message_official_2}' -> {extract_lead_details(test_message_official_2)}")
    # Expected: {'name': 'John Smith', 'email': 'john.smith@innovations.com', 'company': 'Innovations Inc'}
    
    test_message_official_3 = "I want to add a new lead: Michael Brown, michael.brown@another-example.net, from Brown & Co LLC."
    print(f"Official Test 3: '{test_message_official_3}' -> {extract_lead_details(test_message_official_3)}")
    # Expected: {'name': 'Michael Brown', 'email': 'michael.brown@another-example.net', 'company': 'Brown & Co LLC'}

    test_message_official_4 = "Yes, please. Peter Jones at pjones@test.co.uk for Test Ltd"
    print(f"Official Test 4: '{test_message_official_4}' -> {extract_lead_details(test_message_official_4)}")
    # Expected: {'name': 'Peter Jones', 'email': 'pjones@test.co.uk', 'company': 'Test Ltd'}

    test_message_official_5 = "The company is Super Solutions Inc. and the contact is Super Man, superman@supersolutions.com"
    print(f"Official Test 5: '{test_message_official_5}' -> {extract_lead_details(test_message_official_5)}" )
    # Expected: {'name': 'Super Man', 'email': 'superman@supersolutions.com', 'company': 'Super Solutions Inc.'}

    test_message_edge_name_in_company = "Contact is Alex Alex Corp at alex@alexcorp.com from Alex Corp"
    print(f"Edge Case (Name in Company): '{test_message_edge_name_in_company}' -> {extract_lead_details(test_message_edge_name_in_company)}" )
    # Expected: {'name': 'Alex Alex Corp', 'email': 'alex@alexcorp.com', 'company': 'Alex Corp'} -> This is tricky, current logic might make name 'Alex'

    test_message_no_company_suffix = "Reach out to Lead User at lead.user@example.com, company is Example Solutions"
    print(f"No Suffix Test: '{test_message_no_company_suffix}' -> {extract_lead_details(test_message_no_company_suffix)}" )
    # Expected: {'name': 'Lead User', 'email': 'lead.user@example.com', 'company': 'Example Solutions'}

    test_message_name_from_email_only = "Provide info for lead.user@example.com"
    print(f"Name from Email Only Test: '{test_message_name_from_email_only}' -> {extract_lead_details(test_message_name_from_email_only)}" )
    # Expected: {'name': 'Lead User', 'email': 'lead.user@example.com', 'company': None}
    
    test_message_company_keyword_trap = "The lead is Company A, email is contact@companya.com, company is Company A Inc."
    print(f"Company Keyword Trap: '{test_message_company_keyword_trap}' -> {extract_lead_details(test_message_company_keyword_trap)}" )
    # Expected: {'name': 'Company A', 'email': 'contact@companya.com', 'company': 'Company A Inc'}

    test_message_only_email = "new lead: test@example.com"
    print(f"Only Email: '{test_message_only_email}' -> {extract_lead_details(test_message_only_email)}")
    # Expected: {'name': 'Test', 'email': 'test@example.com', 'company': None}

    test_message_name_company_same_word = "Contact Name at name@name.com from Name." # e.g. "Contact Ford at ford@ford.com from Ford."
    print(f"Name/Company Same: '{test_message_name_company_same_word}' -> {extract_lead_details(test_message_name_company_same_word)}")
    # Expected: {'name': 'Name', 'email': 'name@name.com', 'company': 'Name'}

    test_message_email_domain_company = "user@somecompany.com, SomeCompany Ltd"
    print(f"Email domain as company: '{test_message_email_domain_company}' -> {extract_lead_details(test_message_email_domain_company)}")
    # Expected: {'name': 'User', 'email': 'user@somecompany.com', 'company': 'SomeCompany Ltd'}
